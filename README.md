# red_env_launcher

This is an extremely rough demo - **not intended for production use** - of how we can define each of our application environments in a way that hits the requirements listed above:

* Override-able per-project (and potentially at other smaller context levels) without needing to re-define (hey!) the entire configuration.
* Precise control over which packages are resolved for each environment.
* Ability to test versions released off a branch.

### Configuration

Where and how these configuration definitions are sourced from doesn't really matter - for this case I've just written them as YAML documents in the same repo as it's easy to manage. They could be stored in the Ayon database, or another repository. The most important thing is that it is defined in a way that supports sparse overrides, and can be versioned with change history.

The structure of the config files in the repo is:

```yaml
config/
    default/  # The 'variation' of config - we may want to specify other sets, such as staging etc.
        _base.yml  # The studio-level configuration.
        projA.yml  # Project-level overrides for 'projA', that are applied on top of '_base.yml'
        projA_model.yml  # Department level overrides for modelling on 'projA', which are applied on top of 'projA.yml' and '_base.yml'
```

The overrides in that the `{project}.yml` and `{project}_{department}.yml` files are only applied if they exist - so resolving an environment for projB Lookdev for example would just give you the base studio-level configuration.

#### Example

**_base.yml**
```yaml
maya:
    packages:
        maya: '2022.4'
        re_maya_utils: ''
        re_maya_shelves: ''
        re_python_utils: ''
        studiolibrary: ''
        ngskintools: ''
        vrayformaya: ''
```
**projA.yml**
```yaml
maya:
    packages:
        # Lock VRay version for project as it's already started rendering.
        re_maya_utils: '==2.1.0'
```
**projA_model.yml**
```yaml
maya:
    packages:
        re_maya_utils: '<5' # Don't use v5.x.x packages
        re_maya_modeling_tools: ''
```

When you resolve the config for the Model department on projA, you will get:
```yaml
maya:
    packages:
        maya: '2022.4'
        re_maya_utils: '<5'
        re_maya_shelves: ''
        re_maya_modeling_tools: ''
        re_python_utils: ''
        studiolibrary: ''
        ngskintools: ''
        vrayformaya: '==2.1.0'
```

#### What do the values represent in the 'packages' dictionary?

Each key in the 'packages' data represents the name of a Rez package that will be included in that environment (along with all it's dependencies of course).

The value against that key represents a version constraint that will be used when resolving the Rez environment. Each key and value is combined to create a "Package Request". If you're not familiar with Rez package requests you can read about them here: https://github.com/AcademySoftwareFoundation/rez/wiki/Basic-Concepts#package-requests

An empty constraint means that it will allow any packages, and if an operator (`==`, `>`, `<`, etc.) is not specified, the package request will be in the form `{package}-{version}`. So for the resolved configuration above, the following package requests would be sent through to Rez to construct a context:
```
maya-2022.4 re_maya_utils<5 re_maya_shelves re_maya_modeling_tools re_python_utils studiolibrary ngskintools vrayformaya==2.1.0
```

#### What I want to remove a package in an overrides file?

The above example shows how to add new packages and alter the version constraint of existing packages in the config, but what if we want to remove the package altogether? That can be done with an 'exclude' token such as `__exclude__`, that the wrapper tool reading this configuration will interpret as to exclude this package from the package request list. This token can be whatever you want, it just needs to be something that will never be a Rez version constraint. 

As an example, if you want to exclude the `ngskintools` package for the Model department on projA, you can specify:

**projA_model.yml**
```yaml
maya:
    packages:
        re_maya_utils: '<5' # Don't use v5.x.x packages
        re_maya_modeling_tools: ''
        ngskintools: '__exclude__'
```
