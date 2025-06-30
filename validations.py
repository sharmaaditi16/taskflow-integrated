import gladiator as gl

class Validations:

    def __init__(self):
        self.task_validations = (
            ('title', gl.required, gl.length_min(5),gl.length_max(50)),
            ('description', gl.required, gl.length_min(5)),
            ('status', gl.required, gl.type_(str), gl.regex_('^(pending|completed)$')),
            ('due_date', gl.required, gl.type_(str), gl.regex_('^\d{4}-\d{2}-\d{2}$')),
        )
        self.user_validations = (
            ('email', gl.required, gl.regex_('^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')),
            ('password', gl.required, gl.length_min(5),gl.length_max(512)),
            ('username', gl.required, gl.length_min(3), gl.length_max(100))
        )
