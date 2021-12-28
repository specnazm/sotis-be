from testingapp.models.kspacemodels import KnowledgeSpace
from testingapp.models.testmodels import Section
from testingapp import db
import itertools

def save_kspace(iita_kspace, section_ids, domain_id):
    """
    save_kspace creates object of class KnowledgeSpace and store them to db
    If two sections are equivalent only one KnowledgeSpace object is created, its property problem contains id from both equivalent sections.
    In case that section_id has eqivalent ids:
        - If node has been created for any of equivalent id, just add section_id to problem property of that node
        - Otherwise, create new node with problem property containing only section_id

    Adds empty and full state.

    :param iita_kspace: object returned from kst_service, containing implications array
    :param section_ids: array of section ids (Section class), each section represent one problem in domain
    :param domain_id: id of domain (object of class Part)
    :return: /
    """ 
    nodes = {}

    implications = transform_implications(iita_kspace.get("implications"), section_ids)
    equals = find_equal_nodes(implications)
    print("Implications od iite: ", implications)

    implications = remove_duplicate(implications, equals)
    print("Nakon zamene duplikata : ",implications)
    print('Ekvivalentni kljucevi:  ', equals)

    for section_id in section_ids:
        section = Section.query.get(section_id)
        if not section:
            return
        exists = False
        if (is_duplicate(equals, section_id)):
            equivalent_ids = get_eq_list(equals, section_id)
            for eq_id in equivalent_ids:
                if eq_id == section_id: continue
                node = exist_eq_node(nodes.values(), eq_id)
                if node:
                    node.problem.append(section)
                    nodes[section_id] = node
                    exists = True
        if not exists:
            kspace = KnowledgeSpace(
                domain_id=domain_id,
                iita_generated=True,
                )
            kspace.problem.append(section)
            nodes[section_id] = kspace

    nodes = connect_nodes(implications, nodes, equals)
    nodes = set(node for node in nodes.values())

    for node in nodes:
        db.session.add(node)
    
    db.session.commit()
    add_empty(domain_id)
    # add_full(domain_id)

def connect_nodes(implications, nodes, equals):
    """
    connect_nodes sets properties target_problems for each node in nodes array
    If two sections are equivalent no connection is made.
    
    :param nodes: array of KnowledgeSpace objects
    :return: array of KnowledgeSpace objects with defined properties target_problems
    """ 
    for source,target in implications:
        if equivalent(equals, source, target):
            continue
        source_node = nodes[source]
        target_node = nodes[target]

        source_node.target_problems.append(target_node)

    return nodes


def transform_implications(implications, section_ids):
    """
    transform_implications transforms keys from implications array to corresponding section id
    
    :param implications: array of 2-tuple, each tuple represent two ids that are connected, 
            keys in this array are ids from dataframe created (ordinal number of column starting at 0)
    :return: array of 2-tuple, each tuple represent two ids that are connected, 
            keys in this array are section ids
    """ 
    transformed = []
    for source, target in implications:
        transformed.append((section_ids[source], section_ids[target]))

    return transformed

def remove_duplicate(implications, equals):
    """
    remove_duplicate removes one occurence of equivalent keys tuple 
        replaces all occurences of key thah has equivalents to one representative key from that group
    Input [ (2,1), (2,3), (1,2)]
    Output [(1,1), (1,3)]

    :param implications: array of 2-tuple, each tuple represent two ids that are connected
    :param equals: array of tuples, each tuple represent ids that are equivalent among themselves

    :return: array, transformed implications withoud any duplicate
    """ 
    transformed = []
    for source, target in implications:
        if is_duplicate(equals, source):
            source = get_eq_list(equals, source)[0]
        if is_duplicate(equals, target):
            target = get_eq_list(equals, target)[0]
        transformed.append((source, target))

    return set(node for node in transformed)


def find_equal_nodes(implications):
    """
    find_equal_nodes finds equivalent ids in implications
    Transitivity of the = operator is considered. 
        Input example : [(0, 1), (0, 2), (0, 3), (0, 4), (2, 0), (2, 3), (2, 4), (1,2), (3,2), (4,1), (1, 4)]
        Output: [(0,2,3), (4, 1)]

    :param implications: array of 2-tuple, each tuple represent two ids that are equivalent among themselves
    :return: array of n-tuple, each tuple represent n ids that are equivalent among themselves, or [] if there is no equivalent ids
    """ 
    equals = []

    #za svaki node cuva na kom indeksu je dodat u niz equals
    #ako se pronadje duplikat, proverava se da li source ili target vec postoje u nizu equals
    #ako ne postoje samo se doda tuple (source, target) u equals i zabelezi mesto na kom su dodati u niz
    #ako postoji onda se iz added dict uzima na kom mestu je dodat i dodaje se u postojeci tuple
    added = {}
    for i in range(0, len(implications)):
        source, target = implications[i]
        for j in range(i + 1, len(implications)):
            source2, target2 = implications[j]
            if source == target2 and target == source2:
                if source in added.keys():
                    index = added[source]
                    equals[index] += (target,)
                    added[target] = index
                elif target in added.keys():
                    index = added[target]
                    equals[index] += (source,)
                    added[source] = index
                else:
                    equals.append((source, target))
                    #sacuvaj indeks na kom je dodat u niz equals
                    added[source] = len(equals) - 1
                    added[target] = len(equals) - 1
        
    return equals

def is_duplicate(equals, id):
    """
    is_duplicate checks if given id has equivalent ids

    :param equals: array of tuples, each tuple represent ids that are equivalent among themselves
    :param id: id to be found in equals
    :return: True if id has equivalent ids, False otherwise
    """ 
    for tuple in equals:
        if id in tuple:
            return True
    return False

def init_probs(test):
    """
    init_probs initializes field probability of KnowledgeSpace objects
    It is used a priori probability given by formula 1 / number of knowledge spaces
    Only knowledgespaces generated by iita are considered

    :param test: Test object
    :return: list of KnowledgeSpace objects with initialized property probability if test param is defined, None otherwise
    """ 
    if not test:
        return None
    kspace = []
    for part in test.parts:
        nodes = KnowledgeSpace.query.filter_by(domain_id=part.id, iita_generated=True)
        for node in nodes:
            node.probability = (1.0) / nodes.count()
    db.session.commit()

    return kspace

def exist_eq_node(nodes, section_id):
    """
    exist_eq_node tries to find node in array nodes that contains section_id among it's problem field
    Problem field in object of class KnowledgeSpace represents an array of section ids

    :param nodes: array of KnowledgeSpace objects
    :param section_id: id to be found in node's problem field
    :return: node object if exist, None otherwise
    """ 
    for node in nodes:
        for section in node.problem:
            if section_id == section.id:
                return node
    return None

def get_eq_list(equals, id):
    """
    get_eq_list tries to find tuple in equals array that contains id 

    :param equals: array of tuples, each tuple represent ids that are equivalent among themselves
    :param id: id to be found in equals
    :return: tuple of ids that are equivalent to given id, *with* given id or [] if there is no equivalent ids
    """ 
    for ids_tuple in equals:
        if id in ids_tuple:
            return ids_tuple
    return []

def equivalent(equals, key1, key2):
    """
    equivalent checks if keys key1 and key2 are equivalent
    Two keys are considered equivalent if there is one n-tuple in equlas array that contains both keys

    :param equals: array of tuples, each tuple represent ids that are equivalent among themselves
    :param key1: id to be found in equals
    :param key2: id to be found in equals
    :return: True if keys are equivalent, False otherwise
    """ 
    return key1 in get_eq_list(equals, key2)


def add_empty(domain_id=1):
    """
    add_empty adds new KnowledgeSpace object to db, representing empty state

    Empty state indicates to all KnowledgeSpace objects considered as root node
    Root node has source_problems list empty (zero nodes are poiting to root)

    :param domain_id: domain id, id of part representing domain
    :return: /
    """ 
    all = KnowledgeSpace.query.filter_by(domain_id=domain_id)
    roots = []
    for kspace in all:
        if len(kspace.source_problems) == 0:
            roots.append(kspace)
    empty_kspace = KnowledgeSpace(
                domain_id=domain_id,
                iita_generated=True,
                problem=[]
                )
    empty_kspace.target_problems = roots

    db.session.add(empty_kspace)
    db.session.commit()

# def add_full(domain_id=1):
#     """
#     add_full adds new KnowledgeSpace object to db, representing full state
#     Full state can be achieved from any combination of KnowledgeSpace objects that gives full list of problems
#     Full list of problems is the same as all sections for given part (=domain_id)

#     :param domain_id: domain id, id of part representing domain
#     :return: /
#     """ 
#     kspace_list = KnowledgeSpace.query.filter_by(domain_id=domain_id)
#     sections = Section.query.filter_by(part_id=domain_id)
#     full_kspace = KnowledgeSpace(
#                 domain_id=domain_id,
#                 iita_generated=True,
#                 problem=list(sections)
#                 )
#     for sec in sections:
#         print(sec)

#     for size in range(0, kspace_list.count()):
#         for subset in itertools.combinations(kspace_list, size):
#             result = set([])
#             print("=================")
#             for kspace in subset:
#                 # print(set(kspace.problem))
#                 result = result.union(set(kspace.problem))
#                 print()
#                 if len(kspace.problem)> 0 and kspace.problem[0].id == 1:
#                     print("Sekcije u stanju : ", kspace.problem)
#                     print(sections_in_state(kspace))
#                     print()
#                     print()
#             if len(result) == sections.count():
#                 pass
#                 # print("Ova kombinacija daje sve sekcije: ", )
#                 # print(subset)
#                 # for kspace in subset:
#                 #     full_kspace.source_problems.append(kspace)
#     # db.session.add(full_kspace)
#     # db.session.commit()            



# def sections_in_state(state):
#     #is root
#     if len(state.source_problems) == 0:
#         return state.problem
#     else:
#         result = state.problem
#         for parent in state.source_problems:
#             result += sections_in_state(parent)
#         return result
        