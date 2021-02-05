approx
#######

Set of tools for comparing complex objects

.. toctree::
   :maxdepth: 2
   :numbered:
   :hidden:

   user/index
   api/index
   dev/index


Quick Start
===========

approx is available on PyPI and can be installed with `pip <https://pip.pypa.io>`_.

.. code-block:: console

    $ pip install approx

After installing approx you can use it like any other Python module.

Here is a simple example:

.. code-block:: python

   from approx import approx

   item1 = [
       {
           1: [
               {1: [1, 2]},
               [1, 2.0001],
           ],
       },
       [3, [4, [5]]],
   ]

   item2 = [
       {
           1: [
               {1.0001: [1, 2.0001]},
               [1.0001, 1.9999],
           ],
       },
       [2.9999, [4, [5.002]]],
   ]

   assert approx(item1, item2, rel_tol=1e-2)
