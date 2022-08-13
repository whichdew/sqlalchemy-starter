#!/usr/bin/env python3
# coding:utf-8

'''
Author: leoking
Date: 2022-07-13 13:50:35
LastEditTime: 2022-08-13 15:52:52
LastEditors: your name
Description: 
'''

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

try:
    from .todo import Todo, Uri, TodoStatus
except:
    from todo import Todo, Uri, TodoStatus

engine = create_engine('sqlite:///:memory:', echo=True)
Session = sessionmaker(bind=engine)
Todo.metadata.create_all(engine)
Uri.metadata.create_all(engine)


def test_todo():
    uris = [Uri(value='http://www.baidu.com', name='bd')]

    todo = Todo(
        uris=uris,
        title='test',
        status=TodoStatus.TODO,
        # started_at=datetime.now(),
        started_at="2020-07-13 13:50:35",
    )
    session = Session()
    session.add(todo)

    row = session.query(Todo).filter(Todo.title == 'test').one()
    print(row, row.status)
    assert row.uris[0].name == 'bd'


def test_modifier():
    uris = [dict(value='http://www.google.com', name='google')]

    todo = Todo(
        uris=uris,
        title='test1',
        status=TodoStatus.TODO,
        # started_at=datetime.now(),
        started_at="2020-07-13 13:50:35",
    )
    session = Session()
    session.add(todo)

    row = session.query(Todo).filter(Todo.title == 'test1').one()
    print(row, row.status)
    assert row.uris[0].name == 'google'
