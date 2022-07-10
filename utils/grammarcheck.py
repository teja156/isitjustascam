import language_tool_python
tool = language_tool_python.LanguageTool('en-US')

def check(text):
    matches = tool.check(text)
    if len(matches)==0:
        return True
    return False


