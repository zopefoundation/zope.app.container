/*############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
############################################################################*/

#include "Python.h"
#include "persistence/persistence.h"
#include "persistence/persistenceAPI.h"

typedef struct {
  PyPersist_HEAD                 
  PyObject *po_serial;            
  PyObject *po_weaklist;          
  PyObject *proxy_object;
  PyObject *__parent__;
  PyObject *__name__;
} ProxyObject;

typedef struct {
    PyTypeObject *proxytype;
    int (*check)(PyObject *obj);
    PyObject *(*create)(PyObject *obj);
    PyObject *(*getobject)(PyObject *proxy);
} ProxyInterface;

#define Proxy_GET_OBJECT(ob)   (((ProxyObject *)(ob))->proxy_object)

/* Supress inclusion of the original proxy.h */
#define _proxy_H_ 1

/* Incude the proxy C source */
#include "zope/proxy/_zope_proxy_proxy.c"

#define SPECIAL(NAME) (                        \
    *(NAME) == '_' &&                          \
      (((NAME)[1] == 'p' && (NAME)[2] == '_')  \
       ||                                      \
       ((NAME)[1] == '_' && (                  \
         strcmp((NAME), "__parent__") == 0     \
         ||                                    \
         strcmp((NAME), "__name__") == 0       \
         ||                                    \
         strcmp((NAME), "__getstate__") == 0   \
         ||                                    \
         strcmp((NAME), "__setstate__") == 0   \
         ||                                    \
         strcmp((NAME), "__getnewargs__") == 0 \
         ||                                    \
         strcmp((NAME), "__reduce__") == 0     \
         ||                                    \
         strcmp((NAME), "__reduce_ex__") == 0  \
         ))                                    \
       ))
      
static PyObject *
CP_getattro(PyObject *self, PyObject *name)
{
  char *cname;

  cname = PyString_AsString(name);
  if (cname == NULL)
    return NULL;

  if (SPECIAL(cname))
    /* delegate to persistent */
    return PyPersist_TYPE->tp_getattro(self, name);

  /* Use the wrapper version to delegate */
  return wrap_getattro(self, name);
}

static int
CP_setattro(PyObject *self, PyObject *name, PyObject *v)
{
  char *cname;

  cname = PyString_AsString(name);
  if (cname == NULL)
    return -1;

  if (SPECIAL(cname))
    /* delegate to persistent */
    return PyPersist_TYPE->tp_setattro(self, name, v);

  /* Use the wrapper version to delegate */
  return wrap_setattro(self, name, v);
}

static PyObject *
CP_getstate(ProxyObject *self)
{
  return Py_BuildValue("OO", 
                       self->__parent__ ? self->__parent__ : Py_None,
                       self->__name__   ? self->__name__   : Py_None
                       );
}

static PyObject *
CP_getnewargs(ProxyObject *self)
{
  return Py_BuildValue("(O)", self->proxy_object);
}

static PyObject *
CP_setstate(ProxyObject *self, PyObject *state)
{
  if(! PyArg_ParseTuple(state, "OO", &self->__parent__, &self->__name__))
    return NULL;
  Py_INCREF(self->__parent__);
  Py_INCREF(self->__name__);
  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *
CP_reduce(ProxyObject *self)
{
  return Py_BuildValue("O(O)(OO)",
                       self->ob_type,
                       self->proxy_object,
                       self->__parent__ ? self->__parent__ : Py_None,
                       self->__name__   ? self->__name__   : Py_None
                       );
}

static PyObject *
CP_reduce_ex(ProxyObject *self, PyObject *proto)
{
  return CP_reduce(self);
}

static PyObject *
CP__p_deactivate(ProxyObject *self, PyObject *args, PyObject *keywords)
{
    int ghostify = 1;
    PyObject *force = NULL;

    if (args && PyTuple_GET_SIZE(args) > 0) {
	PyErr_SetString(PyExc_TypeError, 
			"_p_deactivate takes not positional arguments");
	return NULL;
    }
    if (keywords) {
	int size = PyDict_Size(keywords);
	force = PyDict_GetItemString(keywords, "force");
	if (force)
	    size--;
	if (size) {
	    PyErr_SetString(PyExc_TypeError, 
			    "_p_deactivate only accepts keyword arg force");
	    return NULL;
	}
    }

    if (self->po_dm && self->po_oid) {
	ghostify = self->po_state == UPTODATE;
	if (!ghostify && force) {
	    if (PyObject_IsTrue(force))
		ghostify = 1;
	    if (PyErr_Occurred())
		return NULL;
	}
	if (ghostify) {
            Py_XDECREF(self->__parent__);
            self->__parent__ = NULL;
            Py_XDECREF(self->__name__);
            self->__name__ = NULL;

	    self->po_state = GHOST;
	}
    }

    Py_INCREF(Py_None);
    return Py_None;
}


static PyMethodDef
CP_methods[] = {
  {"__getstate__", (PyCFunction)CP_getstate, METH_NOARGS, 
   "Get the object state"},
  {"__setstate__", (PyCFunction)CP_setstate, METH_O, 
   "Set the object state"},
  {"__getnewargs__", (PyCFunction)CP_getnewargs, METH_NOARGS, 
   "Get the arguments that must be passed to __new__"},
  {"__reduce__", (PyCFunction)CP_reduce, METH_NOARGS, 
   "Reduce the object to constituent parts."},
  {"__reduce_ex__", (PyCFunction)CP_reduce_ex, METH_O, 
   "Reduce the object to constituent parts."},
  {"_p_deactivate", (PyCFunction)CP__p_deactivate, METH_KEYWORDS, 
   "Deactivate the object."},
  {NULL, NULL},
};


/* Code to access structure members by accessing attributes */

#include "structmember.h"

static PyMemberDef CP_members[] = {
  {"_p_serial", T_OBJECT, offsetof(ProxyObject, po_serial)},
  {"__parent__", T_OBJECT, offsetof(ProxyObject, __parent__)},
  {"__name__", T_OBJECT, offsetof(ProxyObject, __name__)},
  {NULL}	/* Sentinel */
};

static int
CP_traverse(ProxyObject *self, visitproc visit, void *arg)
{
  if (PyPersist_TYPE->tp_traverse((PyObject *)self, visit, arg) < 0)
    return -1;
  if (self->po_serial != NULL && visit(self->po_serial, arg) < 0)
    return -1;
  if (self->proxy_object != NULL && visit(self->proxy_object, arg) < 0)
    return -1;
  if (self->__parent__ != NULL && visit(self->__parent__, arg) < 0)
    return -1;
  if (self->__name__ != NULL && visit(self->__name__, arg) < 0)
    return -1;
  
  return 0;
}

static int
CP_clear(ProxyObject *self)
{
  /* XXXX Drop references that may have created reference
     cycles. Immutable objects do not have to define this method
     since they can never directly create reference cycles. Note
     that the object must still be valid after calling this
     method (don't just call Py_DECREF() on a reference). The
     collector will call this method if it detects that this
     object is involved in a reference cycle.
  */
  PyPersist_TYPE->tp_clear((PyObject*)self);

  Py_XDECREF(self->po_serial);
  self->po_serial = NULL;
  Py_XDECREF(self->proxy_object);
  self->proxy_object = NULL;
  Py_XDECREF(self->__parent__);
  self->__parent__ = NULL;
  Py_XDECREF(self->__name__);
  self->__name__ = NULL;
  return 0;
}

static void
CP_dealloc(ProxyObject *self)
{
  if (self->po_weaklist != NULL)
    PyObject_ClearWeakRefs((PyObject *)self);

  PyObject_GC_UnTrack((PyObject *)self);
  CP_clear(self);
  self->ob_type->tp_free((PyObject*)self);
}

#ifndef PyMODINIT_FUNC	/* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif
PyMODINIT_FUNC
init_zope_app_container_contained(void)
{
  PyObject *m;
        
  /* Try to fake out compiler nag function */
  if (0) init_zope_proxy_proxy();
  
  m = Py_InitModule3("_zope_app_container_contained", 
                     module_functions, module___doc__);

  if (m == NULL)
    return;

  if (empty_tuple == NULL)
    empty_tuple = PyTuple_New(0);

  /* Initialize the PyPersist_C_API and the type objects. */
  PyPersist_C_API = PyCObject_Import("persistence._persistence", "C_API");
  if (PyPersist_C_API == NULL)
    return;

  
  ProxyType.tp_name = "zope.app.container.contained.ContainedProxyBase";
  ProxyType.ob_type = &PyType_Type;
  ProxyType.tp_base = PyPersist_TYPE;
  ProxyType.tp_getattro = CP_getattro;
  ProxyType.tp_setattro = CP_setattro;
  ProxyType.tp_members = CP_members;
  ProxyType.tp_methods = CP_methods;
  ProxyType.tp_traverse = (traverseproc) CP_traverse;
  ProxyType.tp_clear = (inquiry) CP_clear;
  ProxyType.tp_dealloc = (destructor) CP_dealloc;
  ProxyType.tp_weaklistoffset = offsetof(ProxyObject, po_weaklist);

  if (PyType_Ready(&ProxyType) < 0)
    return;

  Py_INCREF(&ProxyType);
  PyModule_AddObject(m, "ContainedProxyBase", (PyObject *)&ProxyType);
}
