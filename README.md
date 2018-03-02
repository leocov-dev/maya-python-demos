# Leo's Maya Python Demos
![tested_maya_2016](https://img.shields.io/badge/maya-2016-128189.svg?style=flat)
![tested_maya_2018](https://img.shields.io/badge/maya-2018-128189.svg?style=flat)
![license](https://img.shields.io/badge/license-MIT-A31F34.svg?style=flat)

## Description

This is a collection of Python tool examples for Maya to share with people looking to learn Python and PySide.  I'll grow this collection as I have time and inspiration.

* qthread_demo
    * This demo shows how to use a QThread to process some operations without blocking Maya's main thread while still updating your UI.

## Installation and Use
1. Place the entire directory for the demo you want to run in your Maya scripts directory or a directory that Maya can load Python scripts from.
    
    ```
    ├- maya
       ├- scripts
          ├- qthread_demo
             ├- __init__.py          
             ├- interface.py
             ├- etc . . .
    ```
    
2. Restart Maya.
3. Launch any tool with the load() method from it's interface.py file:

    ```python
    # EXAMPLE
    # Python
    import qthread_demo.interface as interface
    interface.load()
    ```

##### Notes    

These tools uses the [Qt.py](https://github.com/mottosso/Qt.py) shim to enable compatibility with PySide or PySide2.

I can only test on Windows 10 at the moment. I won't be able to reproduce any issues running on another platform.
