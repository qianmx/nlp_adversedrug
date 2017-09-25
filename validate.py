import argparse
import os
import re
import sys
import time
from xml.etree import ElementTree

VALID_SECTION_NAMES = set(['adverse reactions', 'warnings and precautions',
                          'boxed warnings'])
VALID_MENTION_TYPES = set(['AdverseReaction', 'Severity', 'Factor', 'DrugClass',
                          'Negation', 'Animal'])
VALID_RELATION_TYPES = set(['Hypothetical', 'Effect', 'Negated'])

VALID_MENTION_OFFSETS = re.compile('^[0-9,]+$')

class Label:
  def __init__(self, drug, track):
    self.drug = drug
    self.track = track
    self.sections = []
    self.mentions = []
    self.relations = []
    self.reactions = []

class Section:
  def __init__(self, id, name, text):
    self.id = id
    self.name = name
    self.text = text

class Mention:
  def __init__(self, id, section, type, start, len, str):
    self.id = id
    self.section = section
    self.type = type
    self.start = start
    self.len = len
    self.str = str
  def __str__(self):
    return 'Mention(id={},section={},type={},start={},len={},str="{}")'.format(
        self.id, self.section, self.type, self.start, self.len, self.str)
  def __repr__(self):
    return str(self)

class Relation:
  def __init__(self, id, type, arg1, arg2):
    self.id = id
    self.type = type
    self.arg1 = arg1
    self.arg2 = arg2
  def __str__(self):
    return 'Relation(id={},type={},arg1={},arg2={})'.format(
        self.id, self.type, self.arg1, self.arg2)
  def __repr__(self):
    return str(self)

class Reaction:
  def __init__(self, id, str):
    self.id = id
    self.str = str
    self.normalizations = []

class Normalization:
  def __init__(self, id, meddra_pt, meddra_pt_id, meddra_llt, meddra_llt_id, flag):
    self.id = id
    self.meddra_pt = meddra_pt
    self.meddra_pt_id = meddra_pt_id
    self.meddra_llt = meddra_llt
    self.meddra_llt_id = meddra_llt_id
    self.flag = flag

# Validates the directory
def check_dir(inp_dir):
  files = xml_files(inp_dir)
  for path in files.values():
    print path
    check_file(path)

# Validates the file
def check_file(inp_file):
  label = read(inp_file)
  validate_ind(label)

# Returns all the XML files in a directory as a dict
def xml_files(dir):
  files = {}
  for file in os.listdir(dir):
    if file.endswith('.xml'):
      files[file.replace('.xml', '')] = os.path.join(dir, file)
  return files

# Reads in the XML file
def read(file):
  root = ElementTree.parse(file).getroot()
  assert root.tag == 'Label', 'Root is not Label: ' + root.tag
  label = Label(root.attrib['drug'], root.attrib['track'])
  assert len(root) == 4, 'Expected 4 Children: ' + str(list(root))
  assert root[0].tag == 'Text', 'Expected \'Text\': ' + root[0].tag
  assert root[1].tag == 'Mentions', 'Expected \'Mentions\': ' + root[0].tag
  assert root[2].tag == 'Relations', 'Expected \'Relations\': ' + root[0].tag
  assert root[3].tag == 'Reactions', 'Expected \'Reactions\': ' + root[0].tag

  for elem in root[0]:
    assert elem.tag == 'Section', 'Expected \'Section\': ' + elem.tag
    label.sections.append(
        Section(elem.attrib['id'], \
                elem.attrib['name'], \
                elem.text))

  for elem in root[1]:
    assert elem.tag == 'Mention', 'Expected \'Mention\': ' + elem.tag
    label.mentions.append(
        Mention(elem.attrib['id'], \
                elem.attrib['section'], \
                elem.attrib['type'], \
                elem.attrib['start'], \
                elem.attrib['len'], \
                attrib('str', elem)))

  for elem in root[2]:
    assert elem.tag == 'Relation', 'Expected \'Relation\': ' + elem.tag
    label.relations.append(
        Relation(elem.attrib['id'], \
                 elem.attrib['type'], \
                 elem.attrib['arg1'], \
                 elem.attrib['arg2']))

  for elem in root[3]:
    assert elem.tag == 'Reaction', 'Expected \'Reaction\': ' + elem.tag
    label.reactions.append(
        Reaction(elem.attrib['id'], elem.attrib['str']))
    for elem2 in elem:
      assert elem2.tag == 'Normalization', 'Expected \'Normalization\': ' + elem2.tag
      label.reactions[-1].normalizations.append(
          Normalization(elem2.attrib['id'], \
                        attrib('meddra_pt', elem2), \
                        attrib('meddra_pt_id', elem2), \
                        attrib('meddra_llt', elem2), \
                        attrib('meddra_llt_id', elem2), \
                        attrib('flag', elem2)))

  return label

def attrib(name, elem):
  if name in elem.attrib:
    return elem.attrib[name]
  else:
    return None

# Validates an individual Label
def validate_ind(label):
  sections = {}
  mentions = {}
  relations = {}
  reactions = {}
  for section in label.sections:
    assert section.id.startswith('S'), \
        'Section ID does not start with S: ' + section.id
    assert section.id not in sections, \
        'Duplicate Section ID: ' + section.id
    assert section.name in VALID_SECTION_NAMES, \
        'Invalid Section name: ' + section.name
    sections[section.id] = section
  for mention in label.mentions:
    assert mention.id.startswith('M'), \
        'Mention ID does not start with M: ' + mention.id
    assert mention.id not in mentions, \
        'Duplicate Mention ID: ' + mention.id
    assert mention.section in sections, \
        'No such section in label: ' + mention.section
    assert VALID_MENTION_OFFSETS.match(mention.start), \
        'Invalid start attribute: ' + mention.start
    assert VALID_MENTION_OFFSETS.match(mention.len), \
        'Invalid len attribute: ' + mention.len
    assert mention.type in VALID_MENTION_TYPES, \
        'Invalid Mention type: ' + mention.type
    if mention.str is not None:
      mentions[mention.id] = mention
      text = ''
      for sstart, slen in zip(mention.start.split(','), mention.len.split(',')):
        start = int(sstart)
        end = start + int(slen)
        if len(text) > 0:
          text += ' '
        span = sections[mention.section].text[start:end]
        span = re.sub('\s+', ' ', span)
        text += span
      assert text == mention.str, 'Mention has wrong string value.' + \
          '  From \'str\': \'' + mention.str + '\'' + \
          '  From offsets: \'' + text + '\''
  unique_relations = set()
  for relation in label.relations:
    assert relation.id.startswith('RL'), \
        'Relation ID does not start with RL: ' + relation.id
    assert relation.id not in relations, \
        'Duplicate Relation ID: ' + relation.id
    assert relation.type in VALID_RELATION_TYPES, \
        'Invalid Relation type: ' + relation.type
    assert relation.arg1 in mentions, \
        'Relation ' + relation.id + ' arg1 not in mentions: ' + relation.arg1
    assert relation.arg2 in mentions, \
        'Relation ' + relation.id + ' arg2 not in mentions: ' + relation.arg2
    assert relation.arg1 != relation.arg2, \
        'Relation arguments identical (self-relation)'
    relation_str = relation.type + ':' + relation.arg1 + ':' + relation.arg2
    arg1 = mentions[relation.arg1]
    arg2 = mentions[relation.arg2]
    assert relation_str not in unique_relations, \
        'Duplicate Relation: ' + str(relation) + '\n' + \
        '  Arg1: ' + str(arg1) + '\n' + \
        '  Arg2: ' + str(arg2) + '\n' + \
        '  Label: ' + label.drug + ' ' + \
        str(sections[arg1.section].name)
    unique_relations.add(relation_str)
    relations[relation.id] = relation
  for reaction in label.reactions:
    assert reaction.id.startswith('AR'), \
        'Reaction ID does not start with AR: ' + reaction.id
    assert reaction.id not in reactions, \
        'Duplicate Reaction ID: ' + reaction.id
    assert reaction.str.lower() == reaction.str, \
        'Reaction str is not lower-case: ' + reaction.str
    for normalization in reaction.normalizations:
      assert normalization.id.startswith('AR'), \
          'Normalization ID does not start with AR: ' + normalization.id
      assert normalization.id.find('.N') > 0, \
          'Normalization ID does not contain .N: ' + normalization.id
      assert normalization.meddra_pt or normalization.flag == 'unmapped', \
          'Normalization does not contain meddra_pt and is not unmapped: ' + \
          label.drug + ':' + normalization.id
    reactions[reaction.id] = reaction

if __name__ == '__main__':
  check_dir(sys.argv[1])
  

