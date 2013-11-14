import database as db
import cherrypy
import mako.template
import os
from urllib import urlencode
from cgi import escape as html_escape


column_order = {'Sender':[['id','ip_address','exhibitor_chain','exhibitor_branch','product','version'],
                          ['ID','IP Address','Exhibitor Chain','Exhibitor Branch','Product','Version']],
                'MethodCall':[['id','module','class_name','function'],
                              ['ID','Module','Class Name','Function']],
                'CallStack':[['id','method_call_id','sender_id','total_time','datetime'],
                             ['ID','Method Call',None,'Sender',None,'Total Time','Datetime']],
                'CallStackItem':[['id','call_stack_id','function_name','line_number','module','total_calls','native_calls','cumulative_time','total_time'],
                                 ['ID','Call Stack',None,'Function','Line Number','Module','Total Calls','Native Calls','Cumulative Time','Total Time']],
                'SQLStatement':[['id','sender_id','sql_string','duration','datetime'],
                                ['ID','Sender',None,'SQL','Duration','Datetime']]}


def json_get(table_class, id=None, **kwargs):
    if id:
        kwargs['id'] = id
    kwargs.pop('_', None)
    items = db.session.query(table_class).filter_by(**kwargs).all()
    data = []
    for item in items:
        # item.__dict__.pop('_sa_instance_state', None)
        record = [html_escape(str(item.__dict__[x])) for x in column_order[table_class.__name__][0]]
        data.append(record)
    return {'aaData':data}



class JSONSenders(object):
    exposed = True
    @cherrypy.tools.json_out()
    def GET(self, id=None, **kwargs):
        return json_get(db.Sender, id, **kwargs)

class JSONMethodCalls(object):
    exposed = True
    @cherrypy.tools.json_out()
    def GET(self, id=None, **kwargs):
        return json_get(db.MethodCall, id, **kwargs)

class JSONCallStacks(object):
    exposed = True
    @cherrypy.tools.json_out()
    def GET(self, id=None, **kwargs):
        callstacks = json_get(db.CallStack, id, **kwargs)
        for item in callstacks['aaData'][:]:
            method_call_list = json_get(db.MethodCall, item[1])['aaData'][0]
            sender_list = json_get(db.Sender, item[2])['aaData'][0]
            item[1] = method_call_list
            item[2] = sender_list[1]
            item.insert(2, method_call_list[0])
            item.insert(4, sender_list[0])
        return callstacks

class JSONCallStackItems(object):
    exposed = True
    @cherrypy.tools.json_out()
    def GET(self, id=None, **kwargs):
        callstackitems = json_get(db.CallStackItem, id, **kwargs)
        for item in callstackitems['aaData'][:]:
            item.insert(2, item[1])
        return callstackitems

class JSONSQLStatements(object):
    exposed = True
    @cherrypy.tools.json_out()
    def GET(self, id=None, **kwargs):
        statements = json_get(db.SQLStatement, id, **kwargs)
        for item in statements['aaData'][:]:
            sender_list = json_get(db.Sender, item[1])['aaData'][0]
            item[1] = sender_list[1]
            item.insert(2, sender_list[0])
        return statements








class Senders(object):
    exposed = True

    def GET(self, id=None, **kwargs):
        if id:
            sender = db.session.query(db.Sender).get(id)
            mytemplate = mako.template.Template(filename=os.path.join(os.getcwd(),'static','templates','sender.html'))
            return mytemplate.render(sender=sender,
                                     encoded_kwargs='sender_id=' + str(sender.id)+'&'+urlencode(kwargs))
        else:
            url = cherrypy.serving.request.path_info.split('/')[1]
            mytemplate = mako.template.Template(filename=os.path.join(os.getcwd(),'static','templates','senders.html'))
            return mytemplate.render(url=url, encoded_kwargs=urlencode(kwargs))



class MethodCalls(object):
    exposed = True

    def GET(self, id=None, **kwargs):
        if id:
            method_call = db.session.query(db.MethodCall).get(id)
            mytemplate = mako.template.Template(filename=os.path.join(os.getcwd(),'static','templates','method_call.html'))
            return mytemplate.render(method_call=method_call,
                                     encoded_kwargs='method_call_id=' + str(method_call.id)+'&'+urlencode(kwargs))
        else:
            url = cherrypy.serving.request.path_info.split('/')[1]
            mytemplate = mako.template.Template(filename=os.path.join(os.getcwd(),'static','templates','methodcalls.html'))
            return mytemplate.render(url=url, encoded_kwargs=urlencode(kwargs))



class CallStacks(object):
    exposed = True

    def GET(self, id=None, **kwargs):
        if id:
            call_stack = db.session.query(db.CallStack).get(id)
            mytemplate = mako.template.Template(filename=os.path.join(os.getcwd(),'static','templates','callstack.html'))
            return mytemplate.render(callstack=call_stack,
                                     encoded_kwargs='call_stack_id='+str(call_stack.id)+'&'+urlencode(kwargs))
        else:
            url = cherrypy.serving.request.path_info.split('/')[1]
            mytemplate = mako.template.Template(filename=os.path.join(os.getcwd(),'static','templates','callstacks.html'))
            return mytemplate.render(url=url, encoded_kwargs=urlencode(kwargs))



class SQLStatements(object):
    exposed = True

    def GET(self, **kwargs):
        url = cherrypy.serving.request.path_info.split('/')[1]
        mytemplate = mako.template.Template(filename=os.path.join(os.getcwd(),'static','templates','sqlstatements.html'))
        return mytemplate.render(url=url, encoded_kwargs=urlencode(kwargs))









class Root(object):
    exposed = True

    def GET(self):
        return 'Hello, world.'

    senders = Senders()
    methodcalls = MethodCalls()
    callstacks = CallStacks()
    sqlstatements = SQLStatements()

    _senders = JSONSenders()
    _methodcalls = JSONMethodCalls()
    _callstacks = JSONCallStacks()
    _callstackitems = JSONCallStackItems()
    _sqlstatements = JSONSQLStatements()
