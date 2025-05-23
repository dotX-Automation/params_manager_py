# params_manager_py

Python component to easily manage ROS 2 node parameters through the `rclpy` Python API.

## Contents

If you tried to declare, set, and overall manage a node parameter using the full capabilities of the `rclpy` API, you know it can be a bit of a pain. This library aims to ease the process by providing a simple interface to do so.

The main problem of the `rclpy` is the vast amount of boilerplate code required to declare a parameter, and check its updates during the `on_set_parameters_callback` if required. This library offers an interface to automate all steps, while still provide means to customize the behavior of the node when the parameter is updated.

## Limitations

- Dynamic parameters, *i.e.*, parameters with dynamic typing, are not supported by design.
- The `PManager` class also supports the `BYTE_ARRAY` parameter type, but it does not support automatic declaration at node startup.

## Usage

Two sets of operations must be performed to implement node parameters for a node using this library: writing a few lines of code in your node class to use it, and setting up information to automatically declare the parameters with it.

### Modifying the node

First, you must import the library in your node class. Then, you must declare a `PManager` object in your node class, and initialize it in the constructor, passing to it:

- the pointer to the node object that manages the `PManager`;
- a boolean flag that activates verbose logs upon events such as parameter updates.

Second, you must write a YAML file as reported [below](#configuring-parameters), and place it in a known path which you shall assign to a new string parameter of your node, called `dua.params_file_path`.

Finally, you must call within you node constructor the `init` method of the manager objects, which will look for the YAML file, parse it, register the update callback, and declare the specified parameters.

In case you want to perform a specific action when a specific parameter is updated, you must define a function member (*validator*) for your node with the following signature:

```python
your_validator(p: Parameter) -> bool
```

that has to return `True` if the new parameter value is valid according to your criterion, `False` otherwise. The library approves a parameter update only if all the validators of the parameters involved in the update, if present, return `True`.

With validators and member variables, you have the following options:

- you may specify a member variable without a validator to update the parameter value directly;
- you may specify a validator but not a member variable, to fully control the parameter update yourself (note that this does not prevent you from having a member variable that you update in your validator);
- you may specify both a member variable and a validator, in which case the library will update the member variable with the new value only if the validator returns `True`.

### Configuring parameters

The `params_manager` library can be used to automatically declare the parameters in your node class.

To this end, you have to add a YAML file to the source code of your node, something like the following `params.yaml`:

```yaml
params:
  camera_offset:
    type: double
    default_value: 0.1
    min_value: 0.0
    max_value: 0.5
    step: 0.0
    description: "Distance between camera and drone center"
    constraints: "Can be zero, must be in meters"
    read_only: false
    validator: function_name3 # This is optional

  hsv_from:
    type: integer_array
    default_value:
      - 0
      - 1
    min_value: 0
    max_value: 255
    step: 1
    description: "HSV color lower range"
    constraints: "Can be changed"
    read_only: false
    validator: function_name2 # This is optional

  pub_cv_images:
    type: bool
    default_value: true
    description: "Activates publishers to CV images topic"
    constraints: "Only for testing"
    read_only: true
    validator: function_name1 # This is optional

  area_thr:
    type: integer
    default_value: 5000
    min_value: 1000
    max_value: 300000
    step: 1
    description: "Area threshold"
    constraints: "Cannot be zero"
    read_only: false
    validator: function_name7 # This is optional

  covariances:
    type: double_array
    default_value:
      - 0.0
      - 1.0
      - 2.0
    min_value: 0.0
    max_value: 1000.0
    step: 0.0
    description: "Covariance matrix"
    constraints: "Cannot be changed"
    read_only: true
    validator: function_name6 # This is optional

  bottom_camera_topic_name:
    type: string
    default_value: /usb_camera_driver/bottom_camera/image_rect_color
    description: "Bottom camera topic name"
    constraints: "Cannot be changed"
    read_only: true
    var_name: bottom_camera_topic_name_ # This is optional

  names:
    type: string_array
    default_value:
      - prova1
      - prova2
      - prova3
    description: "Names list"
    constraints: "Cannot be changed"
    read_only: true
    var_name: names_
    validator: function_name99 # This is optional

  bools:
    type: bool_array
    default_value:
      - true
      - false
      - false
    description: "Bool matrix"
    constraints: "Cannot be changed"
    read_only: true
    validator: function_name # This is optional
```

Only fields marked with appropriate comments in the above examples are optional, the rest are mandatory; in particular, each parameter must have a `type` and a `default_value` field, plus other mandatory field that depend on the parameter type; moreover, `var_name` must be the name of a class member variable that can, optionally, be reassigned in real time to the most up-to-date value of the parameter, so as to track it. Note that validator routine names, which can optionally be specified for each parameter, must match those that you may have defined in your node class.

---

## Copyright and License

Copyright 2025 dotX Automation s.r.l.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.

You may obtain a copy of the License at <http://www.apache.org/licenses/LICENSE-2.0>.

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

See the License for the specific language governing permissions and limitations under the License.
