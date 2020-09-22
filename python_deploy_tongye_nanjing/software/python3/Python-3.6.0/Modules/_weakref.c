#include "Python.h"


#define GET_WEAKREFS_LISTPTR(o) \
        ((PyWeakReference **) PyObject_GET_WEAKREFS_LISTPTR(o))

/*[clinic input]
module _weakref
[clinic start generated code]*/
/*[clinic end generated code: output=da39a3ee5e6b4b0d input=ffec73b85846596d]*/

#include "clinic/_weakref.c.h"

/*[clinic input]

_weakref.getweakrefcount -> Py_ssize_t

  object: object
  /

Return the number of weak references to 'object'.
[clinic start generated code]*/

static Py_ssize_t
_weakref_getweakrefcount_impl(PyObject *module, PyObject *object)
/*[clinic end generated code: output=301806d59558ff3e input=cedb69711b6a2507]*/
{
    PyWeakReference **list;

    if (!PyType_SUPPORTS_WEAKREFS(Py_TYPE(object)))
        return 0;

    list = GET_WEAKREFS_LISTPTR(object);
    return _PyWeakref_GetWeakrefCount(*list);
}


PyDoc_STRVAR(weakref_getweakrefs__doc__,
"getweakrefs(object) -- return a list of all weak reference objects\n"
"that point to 'object'.");

static PyObject *
weakref_getweakrefs(PyObject *self, PyObject *object)
{
    PyObject *result = NULL;

    if (PyType_SUPPORTS_WEAKREFS(Py_TYPE(object))) {
        PyWeakReference **list = GET_WEAKREFS_LISTPTR(object);
        Py_ssize_t count = _PyWeakref_GetWeakrefCount(*list);

        result = PyList_New(count);
        if (result != NULL) {
            PyWeakReference *current = *list;
            Py_ssize_t i;
            for (i = 0; i < count; ++i) {
                PyList_SET_ITEM(result, i, (PyObject *) current);
                Py_INCREF(current);
                current = current->wr_next;
            }
        }
    }
    else {
        result = PyList_New(0);
    }
    return result;
}


PyDoc_STRVAR(weakref_proxy__doc__,
"proxy(object[, callback]) -- create a proxy object that weakly\n"
"references 'object'.  'callback', if given, is called with a\n"
"reference to the proxy when 'object' is about to be finalized.");

static PyObject *
weakref_proxy(PyObject *self, PyObject *args)
{
    PyObject *object;
    PyObject *callback = NULL;
    PyObject *result = NULL;

    if (PyArg_UnpackTuple(args, "proxy", 1, 2, &object, &callback)) {
        result = PyWeakref_NewProxy(object, callback);
    }
    return result;
}


static PyMethodDef
weakref_functions[] =  {
    _WEAKREF_GETWEAKREFCOUNT_METHODDEF
    {"getweakrefs",     weakref_getweakrefs,            METH_O,
     weakref_getweakrefs__doc__},
    {"proxy",           weakref_proxy,                  METH_VARARGS,
     weakref_proxy__doc__},
    {NULL, NULL, 0, NULL}
};


static struct PyModuleDef weakrefmodule = {
	PyModuleDef_HEAD_INIT,
	"_weakref",
	"Weak-reference support module.",
	-1,
	weakref_functions,
	NULL,
	NULL,
	NULL,
	NULL
};

PyMODINIT_FUNC
PyInit__weakref(void)
{
    PyObject *m;

    m = PyModule_Create(&weakrefmodule);

    if (m != NULL) {
        Py_INCREF(&_PyWeakref_RefType);
        PyModule_AddObject(m, "ref",
                           (PyObject *) &_PyWeakref_RefType);
        Py_INCREF(&_PyWeakref_RefType);
        PyModule_AddObject(m, "ReferenceType",
                           (PyObject *) &_PyWeakref_RefType);
        Py_INCREF(&_PyWeakref_ProxyType);
        PyModule_AddObject(m, "ProxyType",
                           (PyObject *) &_PyWeakref_ProxyType);
        Py_INCREF(&_PyWeakref_CallableProxyType);
        PyModule_AddObject(m, "CallableProxyType",
                           (PyObject *) &_PyWeakref_CallableProxyType);
    }
    return m;
}
