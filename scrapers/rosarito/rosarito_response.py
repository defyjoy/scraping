from enum import Enum
from typing import List, Optional


class DataNodeName(Enum):
    DATA = "data"


class MetaDataNodeName(Enum):
    SCHEMA = "Schema"


class NameSpace(Enum):
    BASE_POINT_QUANTITY_API = "base/PointQuantityAPI"


class OperationName(Enum):
    FIND_IPWOAC = "findIPWOAC"


class Parameter(Enum):
    ACTUAL = "Actual"
    BEST_AVAIL = "BestAvail"
    GRO = "GRO"
    POINT = "Point"
    POINT_CAPACITY = "Point Capacity"


class Password(Enum):
    NUCDBA = "NUCDBA"


class PortName(Enum):
    POINT_QUANTITY_API_PORT = "PointQuantityAPIPort"


class ServiceName(Enum):
    POINT_QUANTITY_API = "PointQuantityAPI"


class ContentDetail:
    posting_type: int
    attachment_file_identifiers: None
    source: int
    wsdl_url: str
    service_url: str
    name_space: NameSpace
    service_name: ServiceName
    port_name: PortName
    user_name: Password
    password: Password
    operation_name: OperationName
    parameters: List[Optional[Parameter]]
    data_node_name: DataNodeName
    meta_data_node_name: MetaDataNodeName

    def __init__(self, posting_type: int, attachment_file_identifiers: None, source: int, wsdl_url: str,
                 service_url: str, name_space: NameSpace, service_name: ServiceName, port_name: PortName,
                 user_name: Password, password: Password, operation_name: OperationName,
                 parameters: List[Optional[Parameter]], data_node_name: DataNodeName,
                 meta_data_node_name: MetaDataNodeName) -> None:
        self.posting_type = posting_type
        self.attachment_file_identifiers = attachment_file_identifiers
        self.source = source
        self.wsdl_url = wsdl_url
        self.service_url = service_url
        self.name_space = name_space
        self.service_name = service_name
        self.port_name = port_name
        self.user_name = user_name
        self.password = password
        self.operation_name = operation_name
        self.parameters = parameters
        self.data_node_name = data_node_name
        self.meta_data_node_name = meta_data_node_name


class Description(Enum):
    OPERATIONALLY_AVAILABLE_CAPACITY_AS_OF_EFF_DATE = "Operationally Available Capacity as of Eff Date"


class Name(Enum):
    OPERATIONALLY_AVAILABLE_CAPACITY = "Operationally Available Capacity"


class RosaritoResponse:
    add_date: int
    last_update_date: int
    add_user_name: None
    last_update_user_name: None
    posting_id: int
    menu_id: int
    owner_id: int
    name: Name
    description: Description
    posting_type: int
    posting_date: None
    effective_date: int
    roll_off_date: int
    status: int
    content_detail: ContentDetail
    content_filter: None
    posting_template_id: int
    owner_data_definition_id: int
    posting_status_change_audits: None
    menu_detail: None

    def __init__(self, add_date: int, last_update_date: int, add_user_name: None, last_update_user_name: None,
                 posting_id: int, menu_id: int, owner_id: int, name: Name, description: Description, posting_type: int,
                 posting_date: None, effective_date: int, roll_off_date: int, status: int,
                 content_detail: ContentDetail, content_filter: None, posting_template_id: int,
                 owner_data_definition_id: int, posting_status_change_audits: None, menu_detail: None) -> None:
        self.add_date = add_date
        self.last_update_date = last_update_date
        self.add_user_name = add_user_name
        self.last_update_user_name = last_update_user_name
        self.posting_id = posting_id
        self.menu_id = menu_id
        self.owner_id = owner_id
        self.name = name
        self.description = description
        self.posting_type = posting_type
        self.posting_date = posting_date
        self.effective_date = effective_date
        self.roll_off_date = roll_off_date
        self.status = status
        self.content_detail = content_detail
        self.content_filter = content_filter
        self.posting_template_id = posting_template_id
        self.owner_data_definition_id = owner_data_definition_id
        self.posting_status_change_audits = posting_status_change_audits
        self.menu_detail = menu_detail
