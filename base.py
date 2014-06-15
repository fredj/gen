#!/usr/bin/python

# http://genealogy.stackexchange.com/questions/1431/how-do-i-access-my-data-natively-in-gramps


from gramps.gen.dbstate import DbState

from gramps.gen.db import read
from gramps.gen.db import DbBsddb
from gramps.gen.lib import Person

def callback(value):
    pass

dbclass = DbBsddb
dbstate = DbState()
dbstate.change_database(dbclass())
dbstate.db.load('/home/fredj/.gramps/grampsdb/539da728', callback, 'r')


db = dbstate.db

for family in [db.get_family_from_handle(f) for f in db.get_family_handles()]:
    father = db.get_person_from_handle(family.get_father_handle())
    mother = db.get_person_from_handle(family.get_mother_handle())

    print 'pere: ', father.get_primary_name().get_regular_name() if father is not None else '?'
    print 'mere: ', mother.get_primary_name().get_regular_name() if mother is not None else '?'

    marriage_date = None
    for event in [db.get_event_from_handle(e.get_reference_handle()) for e in family.get_event_ref_list()]:
        date = event.get_date_object()
        etype = event.get_type()
        #print 'mariage: ', date if date.is_valid() else '?'
        print etype, date if date.is_valid() else '?'
        if date.is_valid():
            marriage_date = date

    for child in [db.get_person_from_handle(e.get_reference_handle()) for e in family.get_child_ref_list()]:
        birthRef = child.get_birth_ref()
        if birthRef is not None:
            birth = db.get_event_from_handle(birthRef.get_reference_handle())
            date = birth.get_date_object()
            if date.is_valid():
                diff = int(date - marriage_date) if marriage_date is not None else '?'
                print 'naissance: ', date, '-', diff

    print '*' * 80
