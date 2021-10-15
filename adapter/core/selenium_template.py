def initTestNg(data, config):
    targetPartitionUnit = data.targetPartitionUnit  # ? data.targetPartitionUnit : ""
    extension = data.extension  #? data.extension : ""
    methods = ""

    try:
        classes = config["testSuites"][data.testSuite]
        # TODO Add catch exceptions
    
        for method in classes["methods"]:
            method = method["name"]
            methods += f"<include name=\"{method}\" />\n"

        include = f"""
            <class name="{classes["name"]}">
                <methods>
                    {methods}
                </methods>
            </class>"""

        xml = f"""
            <?xml version="1.0" encoding="UTF-8"?>
            <!DOCTYPE suite SYSTEM "http://testng.org/testng-1.0.dtd">
            <suite name="RCV">
                <parameter name="hub" value="{data.ptdAddress}" />
                <parameter name="url" value="{data.url}" />
                <test name="MainFlow">
                    <parameter name="phoneOrEmail" value="{data.phoneOrEmail}" />
                    <parameter name="extension" value="{extension}" />

                    <parameter name="password" value="{data.password}" />
                    <parameter name="pstnPhoneOrEmail" value="{data.phoneOrEmail}" />
                    <parameter name="pstnExtension" value="{extension}" />
                    <parameter name="pstnPassword" value="{data.password}" />

                    <parameter name="dialInNumber" value="16504191505" />
                    <parameter name="targetPartition" value="{targetPartitionUnit}" />

                    <classes>
                        {include}
                    </classes>
                </test>
            </suite>
        """
        return xml
    except:
        return False
    
