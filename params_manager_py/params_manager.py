"""
ROS 2 parameter API wrapper.

dotX Automation s.r.l. <info@dotxautomation.com>

May 15, 2025
"""

# Copyright 2025 dotX Automation s.r.l.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from typing import Any, List

import yaml

from rclpy.node import Node
from rclpy.parameter import Parameter

from rcl_interfaces.msg import IntegerRange, FloatingPointRange
from rcl_interfaces.msg import ParameterDescriptor, ParameterType, SetParametersResult


class PManager:
    """
    Manages ROS 2 node parameters.
    """

    def __init__(self, node: Node, verbose: bool = False) -> None:
        """
        Constructor.

        :param node: Reference to ROS 2 node.
        :param verbose: Verbosity flag.
        """
        self._node = node
        self._params_data = {}
        self._verbose = verbose

        # Register the parameter update callback
        self._node.add_on_set_parameters_callback(self._on_set_parameters_callback)

    def _log_update(self, p: Parameter) -> None:
        """
        Logs successful parameter updates.

        :param p: Updated parameter.
        """
        msg = f"[PARAM] '{p.name}': "
        if p.type_ == ParameterType.PARAMETER_STRING:
            msg += f"'{p.value}'"
        elif p.type_ == ParameterType.PARAMETER_STRING_ARRAY:
            msg += "["
            for i in range(len(p.value)):
                msg += f"'{p.value[i]}'"
                if i != (len(p.value) - 1):
                    msg += ", "
            msg += "]"
        elif p.type_ == ParameterType.PARAMETER_BYTE_ARRAY:
            byte_array = p.value
            first_8 = byte_array[:8]
            last_8 = byte_array[-8:]
            try:
                first_str = first_8.decode('ascii', errors='replace')
                last_str = last_8.decode('ascii', errors='replace')
                msg += f"['{first_str}' ... '{last_str}']"
            except:
                msg += f"['{list(first_8)}' ... '{list(last_8)}']"
        else:
            msg += f"{p.value}"
        self._node.get_logger().info(msg)

    def _on_set_parameters_callback(self, params: List[Parameter]) -> SetParametersResult:
        """
        Parameter update callback.

        :param params: List of parameters to update.
        :return: Parameter update operation result.
        """
        # Initialize result object
        res = SetParametersResult(
            successful=True,
            reason=''
        )

        # Check and update parameters
        for p in params:
            # Check if the parameter is declared and get its data
            p_data = self._params_data.get(p.name, None)
            if p_data is None:
                continue

            # Check type
            if p.type_ != p_data['type']:
                self._node.get_logger().error(
                    f"Parameter '{p.name}' type mismatch")
                res.successful = False
                res.reason = f"Parameter '{p.name}' type mismatch"
                return res

            # Run validator, if present
            validator = getattr(self._node, p_data['validator'], None)
            if validator is not None and callable(validator) and not validator(p):
                self._node.get_logger().error(
                    f"Parameter '{p.name}' update validation failed")
                res.successful = False
                res.reason = f"Parameter '{p.name}' update validation failed"
                return res

            # Update variable, if present
            if hasattr(self._node, p_data['var_name']):
                setattr(self._node, p_data['var_name'], p.value)

            # Log update
            if (self._verbose):
                self._log_update(p)

        return res

    def _add_to_data(
        self,
        name: str,
        type: int,
        var_name: str,
        validator: str
    ) -> None:
        """
        Adds a new set of parameter data to the dictionary.

        :param name: Parameter name.
        :param type: Parameter type.
        :param var_name: Associated node variable name.
        :param validator: Associated node validator name.
        """
        param_data = {}
        param_data['type'] = type
        param_data['var_name'] = var_name
        param_data['validator'] = validator
        self._params_data[name] = param_data

    def _parse_bool_str(self, word: str) -> bool:
        """
        Parses a boolean encoded as a string.

        :param word: Word to parse.
        :return: Boolean value.
        """
        if word == 'true' or word == 'True':
            return True
        elif word == 'false' or word == 'False':
            return False
        else:
            raise ValueError(f"Unknown boolean text representation: {word}")

    def _declare_bool_parameter(
        self,
        name: str,
        default_val: bool,
        desc: str,
        constraints: str,
        read_only: bool,
        var_name: str,
        validator: str
    ) -> None:
        """
        Declares a bool parameter.

        :param name: Parameter name.
        :param default_val: Parameter default value.
        :param desc: Parameter description.
        :param constraints: Parameter additional constraints.
        :param read_only: Parameter read only flag.
        :param var_name: Associated node variable name.
        :param validator: Associated node validator name.
        """
        # Add parameter to the internal database
        self._add_to_data(
            name,
            ParameterType.PARAMETER_BOOL,
            var_name,
            validator
        )

        # Declare parameter
        descriptor = ParameterDescriptor(
            name=name,
            type=ParameterType.PARAMETER_BOOL,
            description=desc,
            additional_constraints=constraints,
            read_only=read_only,
            dynamic_typing=False
        )
        self._node.declare_parameter(name, default_val, descriptor)

    def _declare_bool_array_parameter(
        self,
        name: str,
        default_val: List[bool],
        desc: str,
        constraints: str,
        read_only: bool,
        var_name: str,
        validator: str
    ) -> None:
        """
        Declares a bool array parameter.

        :param name: Parameter name.
        :param default_val: Parameter default value.
        :param desc: Parameter description.
        :param constraints: Parameter additional constraints.
        :param read_only: Parameter read only flag.
        :param var_name: Associated node variable name.
        :param validator: Associated node validator name.
        """
        # Add parameter to the internal database
        self._add_to_data(
            name,
            ParameterType.PARAMETER_BOOL_ARRAY,
            var_name,
            validator
        )

        # Declare parameter
        descriptor = ParameterDescriptor(
            name=name,
            type=ParameterType.PARAMETER_BOOL_ARRAY,
            description=desc,
            additional_constraints=constraints,
            read_only=read_only,
            dynamic_typing=False
        )
        self._node.declare_parameter(name, default_val, descriptor)

    def _declare_integer_parameter(
        self,
        name: str,
        default_val: int,
        from_val: int,
        to_val: int,
        step: int,
        desc: str,
        constraints: str,
        read_only: bool,
        var_name: str,
        validator: str
    ) -> None:
        """
        Declares an integer parameter.

        :param name: Parameter name.
        :param default_val: Parameter default value.
        :param from_val: Parameter value interval left extremum.
        :param to_val: Parameter value interval right extremum.
        :param step: Parameter value interval step.
        :param desc: Parameter description.
        :param constraints: Parameter additional constraints.
        :param read_only: Parameter read only flag.
        :param var_name: Associated node variable name.
        :param validator: Associated node validator name.
        """
        # Add parameter to the internal database
        self._add_to_data(
            name,
            ParameterType.PARAMETER_INTEGER,
            var_name,
            validator
        )

        # Declare parameter
        range = IntegerRange(
            from_value=from_val,
            to_value=to_val,
            step=step
        )
        descriptor = ParameterDescriptor(
            name=name,
            type=ParameterType.PARAMETER_INTEGER,
            description=desc,
            additional_constraints=constraints,
            read_only=read_only,
            dynamic_typing=False,
            integer_range=[range]
        )
        self._node.declare_parameter(name, default_val, descriptor)

    def _declare_integer_array_parameter(
        self,
        name: str,
        default_val: List[int],
        from_val: int,
        to_val: int,
        step: int,
        desc: str,
        constraints: str,
        read_only: bool,
        var_name: str,
        validator: str
    ) -> None:
        """
        Declares an integer array parameter.

        :param name: Parameter name.
        :param default_val: Parameter default value.
        :param from_val: Parameter value interval left extremum.
        :param to_val: Parameter value interval right extremum.
        :param step: Parameter value interval step.
        :param desc: Parameter description.
        :param constraints: Parameter additional constraints.
        :param read_only: Parameter read only flag.
        :param var_name: Associated node variable name.
        :param validator: Associated node validator name.
        """
        # Add parameter to the internal database
        self._add_to_data(
            name,
            ParameterType.PARAMETER_INTEGER_ARRAY,
            var_name,
            validator
        )

        # Declare parameter
        range = IntegerRange(
            from_value=from_val,
            to_value=to_val,
            step=step
        )
        descriptor = ParameterDescriptor(
            name=name,
            type=ParameterType.PARAMETER_INTEGER_ARRAY,
            description=desc,
            additional_constraints=constraints,
            read_only=read_only,
            dynamic_typing=False,
            integer_range=[range]
        )
        self._node.declare_parameter(name, default_val, descriptor)

    def _declare_double_parameter(
        self,
        name: str,
        default_val: float,
        from_val: float,
        to_val: float,
        step: float,
        desc: str,
        constraints: str,
        read_only: bool,
        var_name: str,
        validator: str
    ) -> None:
        """
        Declares a double parameter.

        :param name: Parameter name.
        :param default_val: Parameter default value.
        :param from_val: Parameter value interval left extremum.
        :param to_val: Parameter value interval right extremum.
        :param step: Parameter value interval step.
        :param desc: Parameter description.
        :param constraints: Parameter additional constraints.
        :param read_only: Parameter read only flag.
        :param var_name: Associated node variable name.
        :param validator: Associated node validator name.
        """
        # Add parameter to the internal database
        self._add_to_data(
            name,
            ParameterType.PARAMETER_DOUBLE,
            var_name,
            validator
        )

        # Declare parameter
        range = FloatingPointRange(
            from_value=from_val,
            to_value=to_val,
            step=step
        )
        descriptor = ParameterDescriptor(
            name=name,
            type=ParameterType.PARAMETER_DOUBLE,
            description=desc,
            additional_constraints=constraints,
            read_only=read_only,
            dynamic_typing=False,
            floating_point_range=[range]
        )
        self._node.declare_parameter(name, default_val, descriptor)

    def _declare_double_array_parameter(
        self,
        name: str,
        default_val: List[float],
        from_val: float,
        to_val: float,
        step: float,
        desc: str,
        constraints: str,
        read_only: bool,
        var_name: str,
        validator: str
    ) -> None:
        """
        Declares a double array parameter.

        :param name: Parameter name.
        :param default_val: Parameter default value.
        :param from_val: Parameter value interval left extremum.
        :param to_val: Parameter value interval right extremum.
        :param step: Parameter value interval step.
        :param desc: Parameter description.
        :param constraints: Parameter additional constraints.
        :param read_only: Parameter read only flag.
        :param var_name: Associated node variable name.
        :param validator: Associated node validator name.
        """
        # Add parameter to the internal database
        self._add_to_data(
            name,
            ParameterType.PARAMETER_DOUBLE_ARRAY,
            var_name,
            validator
        )

        # Declare parameter
        range = FloatingPointRange(
            from_value=from_val,
            to_value=to_val,
            step=step
        )
        descriptor = ParameterDescriptor(
            name=name,
            type=ParameterType.PARAMETER_DOUBLE_ARRAY,
            description=desc,
            additional_constraints=constraints,
            read_only=read_only,
            dynamic_typing=False,
            floating_point_range=[range]
        )
        self._node.declare_parameter(name, default_val, descriptor)

    def _declare_string_parameter(
        self,
        name: str,
        default_val: str,
        desc: str,
        constraints: str,
        read_only: bool,
        var_name: str,
        validator: str
    ) -> None:
        """
        Declares a string parameter.

        :param name: Parameter name.
        :param default_val: Parameter default value.
        :param desc: Parameter description.
        :param constraints: Parameter additional constraints.
        :param read_only: Parameter read only flag.
        :param var_name: Associated node variable name.
        :param validator: Associated node validator name.
        """
        # Add parameter to the internal database
        self._add_to_data(
            name,
            ParameterType.PARAMETER_STRING,
            var_name,
            validator
        )

        # Declare parameter
        descriptor = ParameterDescriptor(
            name=name,
            type=ParameterType.PARAMETER_STRING,
            description=desc,
            additional_constraints=constraints,
            read_only=read_only,
            dynamic_typing=False
        )
        self._node.declare_parameter(name, default_val, descriptor)

    def _declare_string_array_parameter(
        self,
        name: str,
        default_val: List[str],
        desc: str,
        constraints: str,
        read_only: bool,
        var_name: str,
        validator: str
    ) -> None:
        """
        Declares a string array parameter.

        :param name: Parameter name.
        :param default_val: Parameter default value.
        :param desc: Parameter description.
        :param constraints: Parameter additional constraints.
        :param read_only: Parameter read only flag.
        :param var_name: Associated node variable name.
        :param validator: Associated node validator name.
        """
        # Add parameter to the internal database
        self._add_to_data(
            name,
            ParameterType.PARAMETER_STRING_ARRAY,
            var_name,
            validator
        )

        # Declare parameter
        descriptor = ParameterDescriptor(
            name=name,
            type=ParameterType.PARAMETER_STRING_ARRAY,
            description=desc,
            additional_constraints=constraints,
            read_only=read_only,
            dynamic_typing=False
        )
        self._node.declare_parameter(name, default_val, descriptor)

    def declare_byte_array_parameter(
        self,
        name: str,
        default_val: bytes,
        desc: str,
        constraints: str,
        read_only: bool,
        var_name: str,
        validator: str
    ) -> None:
        """
        Declares a byte array parameter.

        :param name: Parameter name.
        :param default_val: Parameter default value.
        :param desc: Parameter description.
        :param constraints: Parameter additional constraints.
        :param read_only: Parameter read only flag.
        :param var_name: Associated node variable name.
        :param validator: Associated node validator name.
        """
        # Add parameter to the internal database
        self._add_to_data(
            name,
            ParameterType.PARAMETER_BYTE_ARRAY,
            var_name,
            validator
        )

        # Declare parameter
        descriptor = ParameterDescriptor(
            name=name,
            type=ParameterType.PARAMETER_BYTE_ARRAY,
            description=desc,
            additional_constraints=constraints,
            read_only=read_only,
            dynamic_typing=False
        )
        self._node.declare_parameter(name, default_val, descriptor)

    def _parse_params_file(self, params_file: str) -> None:
        """
        Parses the parameters file and declares all the configured parameters.

        :param params_file: Full path of the parameters configuration YAML file.
        """
        # Start by parsing the YAML contents into a Python object
        try:
            with open(params_file, "r") as f:
                params_yaml = yaml.load(f, Loader=yaml.SafeLoader)
        except FileNotFoundError:
            self._node.get_logger().fatal(f"Parameters file not found: {params_file}")
            raise RuntimeError(
                f"Parameters file not found: {params_file}")
        except yaml.YAMLError as e:
            self._node.get_logger().fatal(f"Invalid YAML in {params_file}: {e}")
            raise RuntimeError(
                f"Invalid YAML in {params_file}: {e}")
        except Exception as e:
            self._node.get_logger().fatal(f"Failed to parse parameters file: {e}")
            raise RuntimeError(
                f"Failed to parse parameters file: {e}")

        if params_yaml is None or 'params' not in params_yaml:
            self._node.get_logger().fatal(
                f"Invalid parameters file: {params_file}")
            raise RuntimeError(
                f"Invalid parameters file: {params_file}")

        # Get ordered params dictionary and declare the parameters
        # This highly depends on the parameter type and YAML parsing
        params_dict = dict(sorted(params_yaml['params'].items()))
        for (param_name, values) in params_dict.items():
            try:
                if values['type'] == 'integer':
                    self._declare_integer_parameter(
                        param_name,
                        int(values['default_value']),
                        int(values['min_value']),
                        int(values['max_value']),
                        int(values['step']),
                        str(values['description']),
                        str(values['constraints']),
                        self._parse_bool_str(str(values['read_only'])),
                        str(values.get('var_name', '')),
                        str(values.get('validator', ''))
                    )
                elif values['type'] == 'double':
                    self._declare_double_parameter(
                        param_name,
                        float(values['default_value']),
                        float(values['min_value']),
                        float(values['max_value']),
                        float(values['step']),
                        str(values['description']),
                        str(values['constraints']),
                        self._parse_bool_str(str(values['read_only'])),
                        str(values.get('var_name', '')),
                        str(values.get('validator', ''))
                    )
                elif values['type'] == 'bool':
                    self._declare_bool_parameter(
                        param_name,
                        self._parse_bool_str(str(values['default_value'])),
                        str(values['description']),
                        str(values['constraints']),
                        self._parse_bool_str(str(values['read_only'])),
                        str(values.get('var_name', '')),
                        str(values.get('validator', ''))
                    )
                elif values['type'] == 'string':
                    self._declare_string_parameter(
                        param_name,
                        str(values['default_value']),
                        str(values['description']),
                        str(values['constraints']),
                        self._parse_bool_str(str(values['read_only'])),
                        str(values.get('var_name', '')),
                        str(values.get('validator', ''))
                    )
                elif values['type'] == 'integer_array':
                    default_values = []
                    for val in list(values['default_value']):
                        default_values.append(int(val))
                    self._declare_integer_array_parameter(
                        param_name,
                        default_values,
                        int(values['min_value']),
                        int(values['max_value']),
                        int(values['step']),
                        str(values['description']),
                        str(values['constraints']),
                        self._parse_bool_str(str(values['read_only'])),
                        str(values.get('var_name', '')),
                        str(values.get('validator', ''))
                    )
                elif values['type'] == 'double_array':
                    default_values = []
                    for val in list(values['default_value']):
                        default_values.append(float(val))
                    self._declare_double_array_parameter(
                        param_name,
                        default_values,
                        float(values['min_value']),
                        float(values['max_value']),
                        float(values['step']),
                        str(values['description']),
                        str(values['constraints']),
                        self._parse_bool_str(str(values['read_only'])),
                        str(values.get('var_name', '')),
                        str(values.get('validator', ''))
                    )
                elif values['type'] == 'bool_array':
                    default_values = []
                    for val in list(values['default_value']):
                        default_values.append(self._parse_bool_str(str(val)))
                    self._declare_bool_array_parameter(
                        param_name,
                        default_values,
                        str(values['description']),
                        str(values['constraints']),
                        self._parse_bool_str(str(values['read_only'])),
                        str(values.get('var_name', '')),
                        str(values.get('validator', ''))
                    )
                elif values['type'] == 'string_array':
                    default_values = []
                    for val in list(values['default_value']):
                        default_values.append(str(val))
                    self._declare_string_array_parameter(
                        param_name,
                        default_values,
                        str(values['description']),
                        str(values['constraints']),
                        self._parse_bool_str(str(values['read_only'])),
                        str(values.get('var_name', '')),
                        str(values.get('validator', ''))
                    )
                else:
                    raise ValueError(
                        f"Unsupported parameter type: {values['type']}")

            except Exception as e:
                raise RuntimeError(
                    f"Failed to parse configuration of parameter {param_name}: {e}")

    def init(self) -> None:
        """
        Initializes the manager and sets the configured node parameters.
        """
        # First, declare the parameters file path as a node parameter and retrieve it
        params_file_path_descriptor = ParameterDescriptor(
            name="dua.params_file_path",
            type=ParameterType.PARAMETER_STRING,
            description="Path to the node parameters configuration YAML file.",
            additional_constraints="Must be a valid file path, if empty parameters are not configured.",
            read_only=True,
            dynamic_typing=False
        )
        params_file_path: str = self._node.declare_parameter(
            "dua.params_file_path",
            "",
            params_file_path_descriptor
        ).value
        if len(params_file_path) == 0:
            return

        # Open and parse the parameters file
        self._parse_params_file(params_file_path)
