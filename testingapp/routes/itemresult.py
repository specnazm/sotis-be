from flask import Blueprint, request, jsonify, Response
from testingapp import db
from testingapp.models.kspacemodels import KnowledgeSpace
from testingapp.models.testmodels import Item, Option, ItemResult, Section
from testingapp.services.kst_services import create_knowledge_space, create_df
from testingapp.services.testing_services import get_next_question, update_rule
from testingapp.utils.authutils import get_user_if_logged_in
from testingapp.services.kspace_service import save_kspace, init_probs, init_probs_by_domain, calc_graph_distance

item_result_bp = Blueprint('itemresult', __name__)


@item_result_bp.route('/itemresult/answer', methods=['POST'])
def create_item_result():
    try:

        # TODO: ovo se mora vratit posle, samo test sad
        user = get_user_if_logged_in()
        if not user:  # or user.role != 'student':
            return Response(status=400)
        user_id = user.id

        # user_id = 5

        data = request.json
        responses = data.get("responses")
        new_result = []

        for item_response in responses:
            is_correct = True
            for option in item_response.get('options'):
                option_obj = Option.query.filter_by(id=option['option_id']).first_or_404()
                is_correct = False if option_obj.is_correct != bool(option["checked"]) else is_correct

            item_id = item_response.get('item_id')
            item_res = ItemResult(is_correct=is_correct, student_id=user_id, item_id=item_id)
            new_result.append(item_res)
            db.session.add(item_res)
            db.session.commit()

        section_id = Item.query.get(item_id).section_id
        domain_id = Section.query.get(section_id).part_id
        update_rule(domain_id, new_result[-1])
        question = get_next_question(domain_id)

        return jsonify(question.to_dict()) if question is not None else Response(status=204)
    except Exception as error:
        print(error)
        return Response(status=400)


@item_result_bp.route('/itemresult', methods=['GET'])
def get_item_results():
    data = request.json
    result_id = request.args.get('result_id')
    items = ItemResult.query.filter_by(id=result_id).all()
    return jsonify([item.to_dict() for item in items])


@item_result_bp.route('/itemresult/generate', methods=['GET'])
def create_ks():
    item_results_query_set = ItemResult.query.all()
    sections_query_set = Section.query.all()

    kspace = KnowledgeSpace.query.filter_by(domain_id=1)
    if kspace.count() == 0:
        keys, df = create_df(sections_query_set, item_results_query_set)
        knowledge_space = create_knowledge_space(df, version=1)

        save_kspace(knowledge_space, list(keys), domain_id=1)
        kspace = KnowledgeSpace.query.filter_by(domain_id=1)

        for node in kspace:
            print(node.problem, node.target_problems)

    return jsonify([node.to_dict(only=("id", "target_problems", "problem")) for node in kspace])


@item_result_bp.route('/itemresult/compare', methods=['GET'])
def compare_ks():
    domain_id = request.args.get('domain_id')

    ks_custom = KnowledgeSpace.query.filter_by(domain_id=domain_id, iita_generated=True)
    ks_exp = KnowledgeSpace.query.filter_by(domain_id=domain_id, iita_generated=False)

    ks_custom_json = [node.to_dict(only=("id", "target_problems", "problem", "probability")) for node in ks_custom]
    ks_exp_json = [node.to_dict(only=("id", "target_problems", "problem", "probability")) for node in ks_exp]

    distance = calc_graph_distance(domain_id)

    return jsonify({"ks_expected": ks_exp_json, "ks_real": ks_custom_json, "distance": distance})
