#!/usr/bin/env python3
# coding:utf-8

'''
Author: leoking
Date: 2022-07-13 13:31:07
LastEditTime: 2022-08-07 19:02:23
LastEditors: your name
Description: 
'''
from datetime import datetime
import enum
from sqlalchemy import (
    JSON,
    DATETIME,
    Column,
    DateTime,
    ForeignKey,
    String,
    Integer,
    Enum,
)
from sqlalchemy.orm import (
    declarative_base,
    relationship,
    declared_attr,
    declarative_mixin,
)
from sqlalchemy.sql import func
from sqlalchemy.event import listen, listens_for


Base = declarative_base()


@declarative_mixin
class BaseMixin:
    """
    约定表名为下划线命名法,带有id/created_at/updated_at/deleted_at字段
    如需自定义命名策略，重载所操作Model的__tablename__方法就行了
    TODO：考虑分离参数Mixin和方法Mixin，这样可进一步解耦
    """

    __abstract__ = True

    # 这里约定__private__存储私有字段名字
    __private__ = []

    __table_args__ = (
        {
            # 'keep_existing': True,
            "keep_existing": True,
        },
    )
    # TODO：装饰器的高级用法
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DATETIME(timezone=True), default=func.now())
    # 在mysql中这里设置on update=CURRENT_TIMESTEMP即可
    # 在sqlite中需要使用触发器
    # 这里使用函数，所以只有通过sqlalchemy调用才可以
    updated_at = Column(
        DATETIME(timezone=True), default=func.now(), onupdate=func.now()
    )
    deleted_at = Column(DATETIME(timezone=True), default=None)

    @declared_attr
    def __tablename__(cls):
        '''
        description: 默认是类名
            TODO：考虑下划线命名法
        param {*} cls
        return {*}
        '''
        return cls.__name__


class Uri(Base, BaseMixin):
    '''
    description: uri
        这里使用了tag而不是category
        TODO：考虑使用关联代理取代功能表外键引用此表
    return {*}
    '''

    # 为了规范，这里强制设置name并且为后面去除uri的衍生表做准备
    name = Column(String(64), nullable=False)
    value = Column(String(256), nullable=False, unique=True)


class TodoStatus(enum.Enum):
    TODO = "todo"
    DOING = "doing"
    DONE = "done"
    CANCELLED = "cancelled"
    # 认为delay可以通过截止日期推算出来
    # DELAYED=4


class Todo(Base, BaseMixin):
    '''
    description:
        代办表,设计为支持多人共用同一条代办
        设计思路：
        1. 同一个人可以拥有多个代办
        2. 多个人可以拥有同一个代办
        3. 必须有开始时间
        4. 不必有结束时间，代表永不结束
        5. 可选的提醒规则
        6. 创建者和users并不矛盾，可以同时存在

    return {*}
    '''

    title = Column(String(64), nullable=False)

    status = Column(Enum(TodoStatus), nullable=False, default=TodoStatus.TODO)

    started_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    location = Column(String(32), nullable=True)

    # uris = relationship(
    #     Uri, secondary='TodoUriMapping', backref='todos', lazy="immediate"
    # )

    uris = relationship(
        Uri, secondary='TodoUriMapping', backref='todos', lazy="immediate"
    )


def str_to_datetime(target, value, oldvalue, initiator):
    '''
    description:
    param {*} target
    param {*} value
    param {*} oldvalue
    param {*} initiator
    return {*}
    '''
    if not value:
        return None
    if type(value) != str:
        return value
    return datetime.strptime(value, '%Y-%m-%d %H:%M:%S')


def format_uris(target, value, oldvalue, initiator):
    '''
    description:
        try to instantiate Uri objects from dict
    param {*} target
    param {*} value
    param {*} oldvalue
    param {*} initiator
    return {*}
    '''
    if not value:
        return []
    return list(map(lambda item: item if isinstance(item, Uri) else Uri(**item), value))


def format_todos(target, value, oldvalue, initiator):
    '''
    description:
        try to instantiate Todo objects from dict
    param {*} target
    param {*} value
    param {*} oldvalue
    param {*} initiator
    return {*}
    '''
    if not value:
        return []
    return list(
        map(lambda item: item if isinstance(item, Todo) else Todo(**item), value)
    )


listen(Todo.started_at, 'set', str_to_datetime, retval=True)
listen(Todo.ended_at, 'set', str_to_datetime, retval=True)
listen(Todo.finished_at, 'set', str_to_datetime, retval=True)
# TODO:为什么不生效？
listen(Todo.uris, "set", format_uris, retval=True)
listen(Uri.todos, "set", format_todos, retval=True)

# listen(Todo.owner, 'set', format_owner, retval=True)


class TodoUriMapping(Base, BaseMixin):
    '''
    description:
    return {*}
    '''

    todo_id = Column(ForeignKey(Todo.id), nullable=False)
    uri_id = Column(ForeignKey(Uri.id), nullable=False)
    # uri = relationship(Uri)
    # todo = relationship(Todo)
