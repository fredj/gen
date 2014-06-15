#!/usr/bin/python

# http://genealogy.stackexchange.com/questions/1431/how-do-i-access-my-data-natively-in-gramps

from __future__ import print_function

from gramps.gen.dbstate import DbState

from gramps.gen.db import read
from gramps.gen.db import DbBsddb
from gramps.gen.lib import Person

def callback(value):
    pass

def has_valid_date(event):
    return event.get_date_object().is_valid()

def is_marriage(event):
    event_type = event.get_type()
    return event_type.value == event_type.MARRIAGE

def is_marriage_banns(event):
    event_type = event.get_type()
    return event_type.value == event_type.MARR_BANNS

dbclass = DbBsddb
dbstate = DbState()
dbstate.change_database(dbclass())
dbstate.db.load('/home/fredj/.gramps/grampsdb/5465dae5', callback, 'r')


db = dbstate.db

print('nom pere,prenom pere,nom mere,prenom mere,date union,type union,naissance premier enfant,difference jours')

for family in [db.get_family_from_handle(f) for f in db.get_family_handles()]:
    # all events with a valid date
    events = filter(has_valid_date, (db.get_event_from_handle(e.get_reference_handle()) for e in family.get_event_ref_list()))

    # find marriage or fallback to banns
    union = next((e for e in events if is_marriage(e)), next((e for e in events if is_marriage_banns(e)), None))

    if union is not None:
        children = (db.get_person_from_handle(e.get_reference_handle()) for e in family.get_child_ref_list())

        birth_dates = []
        for child_birth_ref in filter(None, (child.get_birth_ref() for child in children)):
            birth = db.get_event_from_handle(child_birth_ref.get_reference_handle())
            date = birth.get_date_object()
            if date.is_valid():
                birth_dates.append(date)

        first_child_date = next(iter(sorted(birth_dates)), None)
        if first_child_date is not None:
            father = db.get_person_from_handle(family.get_father_handle()).get_primary_name()
            mother = db.get_person_from_handle(family.get_mother_handle()).get_primary_name()

            print(father.get_surname(), father.get_first_name(), sep=',', end=',')
            print(mother.get_surname(), mother.get_first_name(), sep=',', end=',')
            print(union.get_date_object(), end=',')
            print(union.get_type(), end=',')
            print(first_child_date, end=',')
            print(int(first_child_date - union.get_date_object()), end=',')
            print()
