
def initTestNgJson(data, classes):
    targetPartitionUnit = data.targetPartitionUnit # ? data.targetPartitionUnit : ""
    extension = data.extension # ? data.extension : ""

    """
        <?xml version="1.0" encoding="UTF-8"?>
        <!DOCTYPE suite SYSTEM "http://testng.org/testng-1.0.dtd">
        <suite name="RCV">
            <parameter name="hub" value=data.ptdAddress/>
            <parameter name="url" value=data.url/>
            <test name="MainFlow">
                <parameter name="phoneOrEmail" value=data.phoneOrEmail/>
                <parameter name="extension" value=extension/>

                <parameter name="password" value=data.password/>
                <parameter name="pstnPhoneOrEmail" value=data.phoneOrEmail/>
                <parameter name="pstnExtension" value=extension/>
                <parameter name="pstnPassword" value=data.password/>

                <parameter name="dialInNumber" value="16504191505"/>
                <parameter name="targetPartition" value=targetPartitionUnit/>

                <classes>
                    <class name="com.browserstack.LocalTest"/>
                </classes>
            </test>
        </suite>
    """


    return {
        "_doctype": 'suite SYSTEM "http://testng.org/testng-1.0.dtd" ',
        "suite": {
            
            "@name": "RCV",
            
            "parameter": [
                {

                        "@name": "url",
                        "@value": data.url

                },
                {

                        "@name": "hub",
                        "@value": data.ptdAddress

                }
            ],
            "test": {
                "_attributes": {
                    "name": "MainFlow"
                },
                "parameter": [
                    {
                        "_attributes": {
                            "name": "phoneOrEmail",
                            "value": data.phoneOrEmail
                        }
                    },
                    {
                        "_attributes": {
                            "name": "extension",
                            "value": extension
                        }
                    },
                    {
                        "_attributes": {
                            "name": "password",
                            "value": data.password
                        }
                    },
                    {
                        "_attributes": {
                            "name": "pstnPhoneOrEmail",
                            "value": data.phoneOrEmail
                        }
                    },
                    {
                        "_attributes": {
                            "name": "pstnExtension",
                            "value": extension
                        }
                    },
                    {
                        "_attributes": {
                            "name": "pstnPassword",
                            "value": data.password
                        }
                    },
                    {
                        "_attributes": {
                            "name": "dialInNumber",
                            "value": "16504191505"
                        }
                    },
                    {
                        "_attributes": {
                            "name": "targetPartition",
                            "value": targetPartitionUnit
                        }
                    }
                ],
                "classes": classes
            }
        }
    }


    """
    return {
        "_doctype": 'suite SYSTEM "http://testng.org/testng-1.0.dtd" ',
        "suite": {
            "_attributes": {
                "name": "RCV"
            },
            "parameter": [
                {
                    "_attributes": {
                        "name": "url",
                        "value": data.url
                    }
                },
                {
                    "_attributes": {
                        "name": "hub",
                        "value": data.ptdAddress
                    }
                }
            ],
            "test": {
                "_attributes": {
                    "name": "MainFlow"
                },
                "parameter": [
                    {
                        "_attributes": {
                            "name": "phoneOrEmail",
                            "value": data.phoneOrEmail
                        }
                    },
                    {
                        "_attributes": {
                            "name": "extension",
                            "value": extension
                        }
                    },
                    {
                        "_attributes": {
                            "name": "password",
                            "value": data.password
                        }
                    },
                    {
                        "_attributes": {
                            "name": "pstnPhoneOrEmail",
                            "value": data.phoneOrEmail
                        }
                    },
                    {
                        "_attributes": {
                            "name": "pstnExtension",
                            "value": extension
                        }
                    },
                    {
                        "_attributes": {
                            "name": "pstnPassword",
                            "value": data.password
                        }
                    },
                    {
                        "_attributes": {
                            "name": "dialInNumber",
                            "value": "16504191505"
                        }
                    },
                    {
                        "_attributes": {
                            "name": "targetPartition",
                            "value": targetPartitionUnit
                        }
                    }
                ],
                "classes": classes
            }
        }
    }
    """
