# Copyright (C) 2015 Google Inc., authors, and contributors <see AUTHORS file>
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
# Created By: miha@reciprocitylabs.com
# Maintained By: miha@reciprocitylabs.com

from copy import copy
from os.path import abspath, dirname, join
from random import shuffle

from ggrc import models
from ggrc.converters.import_helper import get_object_column_definitions
from ggrc.converters.import_helper import get_column_order
from ggrc.converters.import_helper import split_array
from ggrc.converters.import_helper import pretty_name
from ggrc.utils import get_mapping_rules
from tests.ggrc import TestCase
from tests.ggrc.generator import ObjectGenerator

THIS_ABS_PATH = abspath(dirname(__file__))
CSV_DIR = join(THIS_ABS_PATH, 'example_csvs/')

def get_mapping_names(class_name):
  mapping_rules = get_mapping_rules()[class_name]
  pretty_rules = map(pretty_name, mapping_rules)
  mapping_names = set(["map:{}".format(name) for name in pretty_rules])
  return mapping_names

class TestSplitArry(TestCase):

  def test_sigle_block(self):
    test_data = [
      ["hello", "world"],
      ["hello", "world"],
      ["hello", "world"],
    ]
    offests, data_blocks = split_array(test_data)
    self.assertEquals(len(data_blocks), 1)
    self.assertEquals(data_blocks[0], test_data)
    self.assertEquals(offests[0], 0)

  def test_sigle_block_with_padding(self):
    test_data = [
      ["", ""],
      ["hello", "world"],
      ["hello", "world", "uet"],
      ["hello", "world"],
      ["hello", "world"],
    ]
    offests, data_blocks = split_array(test_data)
    self.assertEquals(len(data_blocks), 1)
    self.assertEquals(data_blocks[0], test_data[1:])
    self.assertEquals(offests[0], 1)

    test_data = [
      ["", ""],
      ["", ""],
      ["", ""],
      ["hello", "world"],
      ["hello", "world", "uet"],
      ["hello", "world"],
      ["hello", "world"],
      ["", ""],
      ["", ""],
    ]
    offests, data_blocks = split_array(test_data)
    self.assertEquals(len(data_blocks), 1)
    self.assertEquals(data_blocks[0], test_data[3:7])
    self.assertEquals(offests[0], 3)

  def test_multiple_blocks(self):
    test_data = [
      ["", ""],
      ["hello", "world"],
      ["hello", "world", "uet"],
      ["", ""],
      ["hello", "world"],
      ["hello", "world"],
    ]
    offests, data_blocks = split_array(test_data)
    self.assertEquals(len(data_blocks), 2)
    self.assertEquals(data_blocks[0], test_data[1:3])
    self.assertEquals(data_blocks[1], test_data[4:6])
    self.assertEquals(offests[0], 1)
    self.assertEquals(offests[1], 4)

    test_data = [
      ["", ""],
      ["hello", "world"],
      ["hello", "world", "uet"],
      ["hello", "world"],
      ["", ""],
      ["", ""],
      ["hello", "world"],
      ["", ""],
      ["", ""],
      ["hello", "world"],
      ["hello", "world"],
      ["hello", "world"],
    ]
    offests, data_blocks = split_array(test_data)
    self.assertEquals(len(data_blocks), 3)
    self.assertEquals(data_blocks[0], test_data[1:4])
    self.assertEquals(data_blocks[1], test_data[6:7])
    self.assertEquals(data_blocks[2], test_data[9:])
    self.assertEquals(offests[0], 1)
    self.assertEquals(offests[1], 6)
    self.assertEquals(offests[2], 9)




class TestCulumnOrder(TestCase):

  def test_column_order(self):
    attr_list = [
        "slug",
        "title",
        "description",
        "test_plan",
        "notes",
        "owners",
        "start_date",
        "kind",
        "status",
        "url",
        "reference_url",
        "name",
        "email",
        "is_enabled",
        "company",
        "A Capital custom attribute",
        "a simple custom attribute",
        "some custom attribute",
        "map:A thing",
        "map:B thing",
        "map:c thing",
        "map:Program",
        "map:some other mapping",
    ]
    original_list = copy(attr_list)
    for _ in range(1):
      shuffle(attr_list)
      column_order = get_column_order(attr_list)
      self.assertEqual(original_list, column_order)


class TestCustomAttributesDefinitions(TestCase):

  def setUp(self):
    TestCase.setUp(self)
    self.generator = ObjectGenerator()

  def test_policy_definitions(self):
    self.generator.generate_custom_attribute("policy", title="My Attribute")
    self.generator.generate_custom_attribute(
        "policy", title="Mandatory Attribute", mandatory=True)
    definitions = get_object_column_definitions(models.Policy)
    mapping_names = get_mapping_names(models.Policy.__name__)
    display_names = set([val["display_name"] for val in definitions.values()])
    element_names = set([
        "Code",
        "Title",
        "Description",
        "Notes",
        "Owner",
        "Primary Contact",
        "Secondary Contact",
        "Policy URL",
        "Reference URL",
        "Kind/Type",
        "Effective Date",
        "Stop Date",
        "State",
        "My Attribute",
        "Mandatory Attribute",
    ])
    expected_names = element_names.union(mapping_names)
    self.assertEquals(expected_names, display_names)
    vals = {val["display_name"]: val for val in definitions.values()}
    self.assertTrue(vals["Title"]["mandatory"])
    self.assertTrue(vals["Owner"]["mandatory"])
    self.assertTrue(vals["Title"]["unique"])
    self.assertTrue(vals["Mandatory Attribute"]["mandatory"])

  def test_program_definitions(self):
    """ test custom attribute headers for Program """

    self.generator.generate_custom_attribute(
        "program",
        title="My Attribute")
    self.generator.generate_custom_attribute(
        "program",
        title="Mandatory Attribute",
        mandatory=True)
    self.generator.generate_custom_attribute(
        "program",
        title="Choose",
        mandatory=True,
        attribute_type="Dropdown",
        multi_choice="hello,world,what's,up"
    )
    definitions = get_object_column_definitions(models.Program)
    mapping_names = get_mapping_names(models.Program.__name__)
    display_names = set([val["display_name"] for val in definitions.values()])
    element_names = set([
        "Title",
        "Description",
        "Notes",
        "Privacy",
        "Owner",
        "Primary Contact",
        "Secondary Contact",
        "Program URL",
        "Reference URL",
        "Code",
        "Effective Date",
        "Stop Date",
        "State",
        "My Attribute",
        "Mandatory Attribute",
        "Choose",
    ])
    expected_names = element_names.union(mapping_names)
    self.assertEquals(expected_names, display_names)
    vals = {val["display_name"]: val for val in definitions.values()}
    self.assertTrue(vals["Title"]["mandatory"])
    self.assertTrue(vals["Owner"]["mandatory"])
    self.assertTrue(vals["Title"]["unique"])
    self.assertTrue(vals["Mandatory Attribute"]["mandatory"])
    self.assertTrue(vals["Choose"]["mandatory"])
    self.assertTrue(vals["Privacy"]["mandatory"])


class TestGetObjectColumnDefinitions(TestCase):

  """
  Test default column difinitions for all objcts

  order of these test functions is the same as the objects in LHN
  """



  def test_program_definitions(self):
    """ test default headers for Program """
    definitions = get_object_column_definitions(models.Program)
    mapping_names = get_mapping_names(models.Program.__name__)
    display_names = set([val["display_name"] for val in definitions.values()])
    element_names = set([
        "Title",
        "Description",
        "Notes",
        "Privacy",
        "Owner",
        "Primary Contact",
        "Secondary Contact",
        "Program URL",
        "Reference URL",
        "Code",
        "Effective Date",
        "Stop Date",
        "State",
    ])
    expected_names = element_names.union(mapping_names)
    self.assertEquals(expected_names, display_names)
    vals = {val["display_name"]: val for val in definitions.values()}
    self.assertTrue(vals["Title"]["mandatory"])
    self.assertTrue(vals["Owner"]["mandatory"])
    self.assertTrue(vals["Title"]["unique"])

  def test_audit_definitions(self):
    """ test default headers for Audit """
    definitions = get_object_column_definitions(models.Audit)
    mapping_names = get_mapping_names(models.Audit.__name__)
    display_names = set([val["display_name"] for val in definitions.values()])
    element_names = set([
        "Program",
        "Code",
        "Title",
        "Description",
        "Internal Audit Lead",
        "Status",
        "Planned Start Date",
        "Planned End Date",
        "Planned Report Period from",
        "Planned Report Period to",
        "Auditors",
    ])
    expected_names = element_names.union(mapping_names)
    self.assertEquals(expected_names, display_names)
    vals = {val["display_name"]: val for val in definitions.values()}
    self.assertTrue(vals["Title"]["mandatory"])
    self.assertTrue(vals["Title"]["unique"])
    self.assertTrue(vals["Internal Audit Lead"]["mandatory"])

  def test_control_assessment_definitions(self):
    """ test default headers for Control Assessment """
    definitions = get_object_column_definitions(models.ControlAssessment)
    mapping_names = get_mapping_names(models.ControlAssessment.__name__)
    display_names = set([val["display_name"] for val in definitions.values()])
    element_names = set([
        "Title",
        "Description",
        "Notes",
        "Test Plan",
        "Control",
        "Audit",
        "Owner",
        "Primary Contact",
        "Secondary Contact",
        "Assessment URL",
        "Reference URL",
        "Code",
        "Effective Date",
        "Stop Date",
        "State",
        "Conclusion: Design",
        "Conclusion: Operation",
    ])
    expected_names = element_names.union(mapping_names)
    self.assertEquals(expected_names, display_names)
    vals = {val["display_name"]: val for val in definitions.values()}
    self.assertTrue(vals["Title"]["mandatory"])
    self.assertTrue(vals["Owner"]["mandatory"])
    self.assertTrue(vals["Title"]["unique"])
    self.assertTrue(vals["Control"]["mandatory"])
    self.assertTrue(vals["Audit"]["mandatory"])

  def test_issue_definitions(self):
    """ test default headers for Issue """
    definitions = get_object_column_definitions(models.Issue)
    mapping_names = get_mapping_names(models.Issue.__name__)
    display_names = set([val["display_name"] for val in definitions.values()])
    element_names = set([
        "Title",
        "Description",
        "Notes",
        "Test Plan",
        "Owner",
        "Primary Contact",
        "Secondary Contact",
        "Issue URL",
        "Reference URL",
        "Code",
        "Effective Date",
        "Stop Date",
        "State",
    ])
    expected_names = element_names.union(mapping_names)
    self.assertEquals(expected_names, display_names)
    vals = {val["display_name"]: val for val in definitions.values()}
    self.assertTrue(vals["Title"]["mandatory"])
    self.assertTrue(vals["Owner"]["mandatory"])
    self.assertTrue(vals["Title"]["unique"])

  def test_regulation_definitions(self):
    """ test default headers for Regulation """
    definitions = get_object_column_definitions(models.Regulation)
    mapping_names = get_mapping_names(models.Regulation.__name__)
    display_names = set([val["display_name"] for val in definitions.values()])
    element_names = set([
        "Title",
        "Description",
        "Notes",
        "Owner",
        "Primary Contact",
        "Secondary Contact",
        "Regulation URL",
        "Reference URL",
        "Code",
        "Effective Date",
        "Stop Date",
        "State",
    ])
    expected_names = element_names.union(mapping_names)
    self.assertEquals(expected_names, display_names)
    vals = {val["display_name"]: val for val in definitions.values()}
    self.assertTrue(vals["Title"]["mandatory"])
    self.assertTrue(vals["Owner"]["mandatory"])
    self.assertTrue(vals["Title"]["unique"])

  def test_policy_definitions(self):
    """ test default headers for Policy """
    definitions = get_object_column_definitions(models.Policy)
    mapping_names = get_mapping_names(models.Policy.__name__)
    display_names = set([val["display_name"] for val in definitions.values()])
    element_names = set([
        "Title",
        "Description",
        "Notes",
        "Owner",
        "Primary Contact",
        "Secondary Contact",
        "Policy URL",
        "Reference URL",
        "Kind/Type",
        "Code",
        "Effective Date",
        "Stop Date",
        "State",
    ])
    expected_names = element_names.union(mapping_names)
    self.assertEquals(expected_names, display_names)
    vals = {val["display_name"]: val for val in definitions.values()}
    self.assertTrue(vals["Title"]["mandatory"])
    self.assertTrue(vals["Owner"]["mandatory"])
    self.assertTrue(vals["Title"]["unique"])

  def test_standard_definitions(self):
    """ test default headers for Standard """
    definitions = get_object_column_definitions(models.Standard)
    mapping_names = get_mapping_names(models.Standard.__name__)
    display_names = set([val["display_name"] for val in definitions.values()])
    element_names = set([
        "Title",
        "Description",
        "Notes",
        "Owner",
        "Primary Contact",
        "Secondary Contact",
        "Standard URL",
        "Reference URL",
        "Code",
        "Effective Date",
        "Stop Date",
        "State",
    ])
    expected_names = element_names.union(mapping_names)
    self.assertEquals(expected_names, display_names)
    vals = {val["display_name"]: val for val in definitions.values()}
    self.assertTrue(vals["Title"]["mandatory"])
    self.assertTrue(vals["Owner"]["mandatory"])
    self.assertTrue(vals["Title"]["unique"])

  def test_contract_definitions(self):
    """ test default headers for Contract """
    definitions = get_object_column_definitions(models.Contract)
    mapping_names = get_mapping_names(models.Contract.__name__)
    display_names = set([val["display_name"] for val in definitions.values()])
    element_names = set([
        "Title",
        "Description",
        "Notes",
        "Owner",
        "Primary Contact",
        "Secondary Contact",
        "Contract URL",
        "Reference URL",
        "Code",
        "Effective Date",
        "Stop Date",
        "State",
    ])
    expected_names = element_names.union(mapping_names)
    self.assertEquals(expected_names, display_names)
    vals = {val["display_name"]: val for val in definitions.values()}
    self.assertTrue(vals["Title"]["mandatory"])
    self.assertTrue(vals["Owner"]["mandatory"])
    self.assertTrue(vals["Title"]["unique"])

  def test_clause_definitions(self):
    """ test default headers for Clause """
    definitions = get_object_column_definitions(models.Clause)
    mapping_names = get_mapping_names(models.Clause.__name__)
    display_names = set([val["display_name"] for val in definitions.values()])
    element_names = set([
        "Title",
        "Description",
        "Notes",
        "Owner",
        "Primary Contact",
        "Secondary Contact",
        "Clause URL",
        "Reference URL",
        "Code",
        "Effective Date",
        "Stop Date",
        "State",
    ])
    expected_names = element_names.union(mapping_names)
    self.assertEquals(expected_names, display_names)
    vals = {val["display_name"]: val for val in definitions.values()}
    self.assertTrue(vals["Title"]["mandatory"])
    self.assertTrue(vals["Owner"]["mandatory"])
    # self.assertTrue(vals["Title"]["unique"])

  def test_section_definitions(self):
    """ test default headers for Section """
    definitions = get_object_column_definitions(models.Section)
    mapping_names = get_mapping_names(models.Section.__name__)
    display_names = set([val["display_name"] for val in definitions.values()])
    element_names = set([
        "Title",
        "Text of Section",
        "Notes",
        "Policy / Regulation / Standard",
        "Owner",
        "Primary Contact",
        "Secondary Contact",
        "Section URL",
        "Reference URL",
        "Code",
        "State",
    ])
    expected_names = element_names.union(mapping_names)
    self.assertEquals(expected_names, display_names)
    vals = {val["display_name"]: val for val in definitions.values()}
    self.assertTrue(vals["Title"]["mandatory"])
    self.assertTrue(vals["Owner"]["mandatory"])
    # self.assertTrue(vals["Title"]["unique"])

  def test_control_definitions(self):
    """ test default headers for Control """
    definitions = get_object_column_definitions(models.Control)
    mapping_names = get_mapping_names(models.Control.__name__)
    display_names = set([val["display_name"] for val in definitions.values()])
    element_names = set([
        "Title",
        "Description",
        "Test Plan",
        "Notes",
        "Owner",
        "Primary Contact",
        "Secondary Contact",
        "Control URL",
        "Reference URL",
        "Code",
        "Kind/Nature",
        "Fraud Related",
        "Significance",
        "Type/Means",
        "Effective Date",
        "Stop Date",
        "Frequency",
        "Assertions",
        "Categories",
        "Principal Assessor",
        "Secondary Assessor",
        "State",
    ])
    expected_names = element_names.union(mapping_names)
    self.assertEquals(expected_names, display_names)
    vals = {val["display_name"]: val for val in definitions.values()}
    self.assertTrue(vals["Title"]["mandatory"])
    self.assertTrue(vals["Owner"]["mandatory"])
    self.assertTrue(vals["Title"]["unique"])

  def test_objective_definitions(self):
    """ test default headers for Objective """
    definitions = get_object_column_definitions(models.Objective)
    mapping_names = get_mapping_names(models.Objective.__name__)
    display_names = set([val["display_name"] for val in definitions.values()])
    element_names = set([
        "Title",
        "Description",
        "Notes",
        "Owner",
        "Primary Contact",
        "Secondary Contact",
        "Objective URL",
        "Reference URL",
        "Code",
        "State",
    ])
    expected_names = element_names.union(mapping_names)
    self.assertEquals(expected_names, display_names)
    vals = {val["display_name"]: val for val in definitions.values()}
    self.assertTrue(vals["Title"]["mandatory"])
    self.assertTrue(vals["Owner"]["mandatory"])
    self.assertTrue(vals["Title"]["unique"])

  def test_person_definitions(self):
    """ test default headers for Person """
    definitions = get_object_column_definitions(models.Person)
    mapping_names = get_mapping_names(models.Person.__name__)
    display_names = set([val["display_name"] for val in definitions.values()])
    element_names = set([
        "Name",
        "Email",
        "Company",
    ])
    expected_names = element_names.union(mapping_names)
    self.assertEquals(expected_names, display_names)
    vals = {val["display_name"]: val for val in definitions.values()}
    self.assertTrue(vals["Email"]["mandatory"])
    self.assertTrue(vals["Email"]["unique"])

  def test_org_group_definitions(self):
    """ test default headers for OrgGroup """
    definitions = get_object_column_definitions(models.OrgGroup)
    mapping_names = get_mapping_names(models.OrgGroup.__name__)
    display_names = set([val["display_name"] for val in definitions.values()])
    element_names = set([
        "Title",
        "Description",
        "Notes",
        "Owner",
        "Primary Contact",
        "Secondary Contact",
        "Org Group URL",
        "Reference URL",
        "Code",
        "Effective Date",
        "Stop Date",
        "State",
    ])
    expected_names = element_names.union(mapping_names)
    self.assertEquals(expected_names, display_names)
    vals = {val["display_name"]: val for val in definitions.values()}
    self.assertTrue(vals["Title"]["mandatory"])
    self.assertTrue(vals["Owner"]["mandatory"])
    self.assertTrue(vals["Title"]["unique"])

  def test_vendor_definitions(self):
    """ test default headers for Vendor """
    definitions = get_object_column_definitions(models.Vendor)
    mapping_names = get_mapping_names(models.Vendor.__name__)
    display_names = set([val["display_name"] for val in definitions.values()])
    element_names = set([
        "Title",
        "Description",
        "Notes",
        "Owner",
        "Primary Contact",
        "Secondary Contact",
        "Vendor URL",
        "Reference URL",
        "Code",
        "Effective Date",
        "Stop Date",
        "State",
    ])
    expected_names = element_names.union(mapping_names)
    self.assertEquals(expected_names, display_names)
    vals = {val["display_name"]: val for val in definitions.values()}
    self.assertTrue(vals["Title"]["mandatory"])
    self.assertTrue(vals["Owner"]["mandatory"])
    self.assertTrue(vals["Title"]["unique"])

  def test_system_definitions(self):
    """ test default headers for System """
    definitions = get_object_column_definitions(models.System)
    mapping_names = get_mapping_names(models.System.__name__)
    display_names = set([val["display_name"] for val in definitions.values()])
    element_names = set([
        "Title",
        "Description",
        "Notes",
        "Owner",
        "Primary Contact",
        "Secondary Contact",
        "System URL",
        "Reference URL",
        "Code",
        "Network Zone",
        "Effective Date",
        "Stop Date",
        "State",
    ])
    expected_names = element_names.union(mapping_names)
    self.assertEquals(expected_names, display_names)
    vals = {val["display_name"]: val for val in definitions.values()}
    self.assertTrue(vals["Title"]["mandatory"])
    self.assertTrue(vals["Owner"]["mandatory"])
    self.assertTrue(vals["Title"]["unique"])

  def test_process_definitions(self):
    """ test default headers for Process """
    definitions = get_object_column_definitions(models.Process)
    mapping_names = get_mapping_names(models.Process.__name__)
    display_names = set([val["display_name"] for val in definitions.values()])
    element_names = set([
        "Title",
        "Description",
        "Notes",
        "Owner",
        "Primary Contact",
        "Secondary Contact",
        "Process URL",
        "Reference URL",
        "Code",
        "Network Zone",
        "Effective Date",
        "Stop Date",
        "State",
    ])
    expected_names = element_names.union(mapping_names)
    self.assertEquals(expected_names, display_names)
    vals = {val["display_name"]: val for val in definitions.values()}
    self.assertTrue(vals["Title"]["mandatory"])
    self.assertTrue(vals["Owner"]["mandatory"])
    self.assertTrue(vals["Title"]["unique"])

  def test_data_asset_definitions(self):
    """ test default headers for DataAsset """
    definitions = get_object_column_definitions(models.DataAsset)
    mapping_names = get_mapping_names(models.DataAsset.__name__)
    display_names = set([val["display_name"] for val in definitions.values()])
    element_names = set([
        "Title",
        "Description",
        "Notes",
        "Owner",
        "Primary Contact",
        "Secondary Contact",
        "Data Asset URL",
        "Reference URL",
        "Code",
        "Effective Date",
        "Stop Date",
        "State",
    ])
    expected_names = element_names.union(mapping_names)
    self.assertEquals(expected_names, display_names)
    vals = {val["display_name"]: val for val in definitions.values()}
    self.assertTrue(vals["Title"]["mandatory"])
    self.assertTrue(vals["Owner"]["mandatory"])
    self.assertTrue(vals["Title"]["unique"])

  def test_product_definitions(self):
    """ test default headers for Product """
    definitions = get_object_column_definitions(models.Product)
    mapping_names = get_mapping_names(models.Product.__name__)
    display_names = set([val["display_name"] for val in definitions.values()])
    element_names = set([
        "Title",
        "Description",
        "Notes",
        "Owner",
        "Primary Contact",
        "Secondary Contact",
        "Product URL",
        "Reference URL",
        "Code",
        "Kind/Type",
        "Effective Date",
        "Stop Date",
        "State",
    ])
    expected_names = element_names.union(mapping_names)
    self.assertEquals(expected_names, display_names)
    vals = {val["display_name"]: val for val in definitions.values()}
    self.assertTrue(vals["Title"]["mandatory"])
    self.assertTrue(vals["Owner"]["mandatory"])
    self.assertTrue(vals["Title"]["unique"])

  def test_project_definitions(self):
    """ test default headers for Project """
    definitions = get_object_column_definitions(models.Project)
    mapping_names = get_mapping_names(models.Project.__name__)
    display_names = set([val["display_name"] for val in definitions.values()])
    element_names = set([
        "Title",
        "Description",
        "Notes",
        "Owner",
        "Primary Contact",
        "Secondary Contact",
        "Project URL",
        "Reference URL",
        "Code",
        "Effective Date",
        "Stop Date",
        "State",
    ])
    expected_names = element_names.union(mapping_names)
    self.assertEquals(expected_names, display_names)
    vals = {val["display_name"]: val for val in definitions.values()}
    self.assertTrue(vals["Title"]["mandatory"])
    self.assertTrue(vals["Owner"]["mandatory"])
    self.assertTrue(vals["Title"]["unique"])

  def test_facility_definitions(self):
    """ test default headers for Facility """
    definitions = get_object_column_definitions(models.Facility)
    mapping_names = get_mapping_names(models.Facility.__name__)
    display_names = set([val["display_name"] for val in definitions.values()])
    element_names = set([
        "Title",
        "Description",
        "Notes",
        "Owner",
        "Primary Contact",
        "Secondary Contact",
        "Facility URL",
        "Reference URL",
        "Code",
        "Effective Date",
        "Stop Date",
        "State",
    ])
    expected_names = element_names.union(mapping_names)
    self.assertEquals(expected_names, display_names)
    vals = {val["display_name"]: val for val in definitions.values()}
    self.assertTrue(vals["Title"]["mandatory"])
    self.assertTrue(vals["Owner"]["mandatory"])
    self.assertTrue(vals["Title"]["unique"])

  def test_market_definitions(self):
    """ test default headers for Market """
    definitions = get_object_column_definitions(models.Market)
    mapping_names = get_mapping_names(models.Market.__name__)
    display_names = set([val["display_name"] for val in definitions.values()])
    element_names = set([
        "Title",
        "Description",
        "Notes",
        "Owner",
        "Primary Contact",
        "Secondary Contact",
        "Market URL",
        "Reference URL",
        "Code",
        "Effective Date",
        "Stop Date",
        "State",
    ])
    expected_names = element_names.union(mapping_names)
    self.assertEquals(expected_names, display_names)
    vals = {val["display_name"]: val for val in definitions.values()}
    self.assertTrue(vals["Title"]["mandatory"])
    self.assertTrue(vals["Owner"]["mandatory"])
    self.assertTrue(vals["Title"]["unique"])