from flask import Blueprint, request, jsonify, Response
from testingapp import db
from testingapp.models.testmodels import Item, Option, ItemResult
from testingapp.services.kst_services import create_knowledge_space, create_df
from testingapp.utils.authutils import get_user_if_logged_in

item_result_bp = Blueprint('itemresult', __name__)


@item_result_bp.route('/itemresult', methods=['POST'])
def create_item_result():
    try:
        user = get_user_if_logged_in()
        if not user: #or user.role != 'student':
            return Response(status=400)

        data = request.json
        responses = data.get("reponses")
        for item_response in responses:
            is_correct = True
            for option in item_response.get('options'):
                option_obj = Option.query.filter_by(id=option['option_id']).first_or_404()
                is_correct = False if option_obj.is_correct != bool(option["checked"]) else is_correct

            item_id = item_response.get('item_id')
            new_result = ItemResult(is_correct=is_correct, student_id=user.id, item_id=item_id)

            db.session.add(new_result)
            db.session.commit()
        
        return Response(status=200)
    except Exception as error:
        print(error)
        return Response(status=400)


@item_result_bp.route('/itemresult', methods=['GET'])
def get_item_results():
    data = request.json
    result_id = request.args.get('result_id')
    items = ItemResult.query.filter_by(id=result_id).all()
    return jsonify([item.to_dict() for item in items])

@item_result_bp.route('/item-result/generate', methods=['GET'])
def create_ks():
    query_set = ItemResult.query.all()

    df = create_df(query_set)
    knowledge_space = create_knowledge_space(df, version=1)
    print(knowledge_space)

    return Response(status=200)