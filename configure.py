#!/usr/bin/env python
"""
Runbook to configure datacenter
"""
from brigade.core import InitBrigade
from brigade.plugins.functions.text import (
    print_result, print_title
)
from brigade.plugins.tasks.data import load_yaml
from brigade.plugins.tasks.networking import napalm_configure
from brigade.plugins.tasks.text import template_file


def configure(task):
    """
    This function groups all the tasks needed to configure the
    network:
        1. Load data
        2. Use templates to build configuration
        3. Deploy configuration on the devices
    """
    r = task.run(
        name="Loading data",
        task=load_yaml,
        file=f"data/{task.host}/l3.yaml",
    )
    # r.result holds the data contained in the yaml files
    # we load the data inside the host itself for further use
    task.host["l3"] = r.result

    r = task.run(
        name="Interface Configuration",
        task=template_file,
        template="interfaces.j2",
        path=f"templates",
    )
    # we append the generated configuration
    config += r.result

    r = task.run(
        name="OSPF Configuration",
        task=template_file,
        template="ospf.js",
        path=f"templates",
    )
    config += r.result

    task.run(
        name="Loading Configuration on the device",
        task=napalm_configure,
        replace=False,
        configuration=config,
    )


# Initialize brigade
brg = InitBrigade(
    dry_run=True, num_workers=20
)


# Let's just filter the hosts we want to operate on
target = brg.filter(type="router")

# Let's call the grouped tasks defined above
results = target.run(task=configure)

# Let's show everything on screen
print_title("Playbook to configure the network")
print_result(results)