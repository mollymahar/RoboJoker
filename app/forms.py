from flask.ext.wtf import Form
from wtforms import StringField, IntegerField, PasswordField, RadioField, DateField, HiddenField
from flask_wtf.html5 import EmailField
from wtforms import validators

# baseline form
class QuestionForm(Form):

    q1 = RadioField('Joke 1', [validators.optional()], choices=[('1','&#9733; (not funny at all)'),
    ('2','&#9733; &#9733;'), ('3','&#9733; &#9733; &#9733; (somewhat funny)'),
    ('4','&#9733; &#9733; &#9733; &#9733;'), ('5','&#9733; &#9733; &#9733; &#9733; &#9733; (very funny)')])

    q2 = RadioField('Joke 2', [validators.optional()], choices=[('1','&#9733; (not funny at all)'),
    ('2','&#9733; &#9733;'), ('3','&#9733; &#9733; &#9733; (somewhat funny)'),
    ('4','&#9733; &#9733; &#9733; &#9733;'), ('5','&#9733; &#9733; &#9733; &#9733; &#9733; (very funny)')])

    q3 = RadioField('Joke 3', [validators.optional()], choices=[('1','&#9733; (not funny at all)'),
    ('2','&#9733; &#9733;'), ('3','&#9733; &#9733; &#9733; (somewhat funny)'),
    ('4','&#9733; &#9733; &#9733; &#9733;'), ('5','&#9733; &#9733; &#9733; &#9733; &#9733; (very funny)')])

    q4 = RadioField('Joke 4', [validators.optional()], choices=[('1','&#9733; (not funny at all)'),
    ('2','&#9733; &#9733;'), ('3','&#9733; &#9733; &#9733; (somewhat funny)'),
    ('4','&#9733; &#9733; &#9733; &#9733;'), ('5','&#9733; &#9733; &#9733; &#9733; &#9733; (very funny)')])

    q5 = RadioField('Joke 5', [validators.optional()], choices=[('1','&#9733; (not funny at all)'),
    ('2','&#9733; &#9733;'), ('3','&#9733; &#9733; &#9733; (somewhat funny)'),
    ('4','&#9733; &#9733; &#9733; &#9733;'), ('5','&#9733; &#9733; &#9733; &#9733; &#9733; (very funny)')])

# evaluation form
class EvaluateForm(Form):

    q1 = RadioField('Joke 1', [validators.optional()], choices=[('1','&#9733; (not funny at all)'),
    ('2','&#9733; &#9733;'), ('3','&#9733; &#9733; &#9733; (somewhat funny)'),
    ('4','&#9733; &#9733; &#9733; &#9733;'), ('5','&#9733; &#9733; &#9733; &#9733; &#9733; (very funny)')])

    q2 = RadioField('Joke 2', [validators.optional()], choices=[('1','&#9733; (not funny at all)'),
    ('2','&#9733; &#9733;'), ('3','&#9733; &#9733; &#9733; (somewhat funny)'),
    ('4','&#9733; &#9733; &#9733; &#9733;'), ('5','&#9733; &#9733; &#9733; &#9733; &#9733; (very funny)')])

    q3 = RadioField('Joke 3', [validators.optional()], choices=[('1','&#9733; (not funny at all)'),
    ('2','&#9733; &#9733;'), ('3','&#9733; &#9733; &#9733; (somewhat funny)'),
    ('4','&#9733; &#9733; &#9733; &#9733;'), ('5','&#9733; &#9733; &#9733; &#9733; &#9733; (very funny)')])

    q4 = RadioField('Joke 4', [validators.optional()], choices=[('1','&#9733; (not funny at all)'),
    ('2','&#9733; &#9733;'), ('3','&#9733; &#9733; &#9733; (somewhat funny)'),
    ('4','&#9733; &#9733; &#9733; &#9733;'), ('5','&#9733; &#9733; &#9733; &#9733; &#9733; (very funny)')])

    q5 = RadioField('Joke 5', [validators.optional()], choices=[('1','&#9733; (not funny at all)'),
    ('2','&#9733; &#9733;'), ('3','&#9733; &#9733; &#9733; (somewhat funny)'),
    ('4','&#9733; &#9733; &#9733; &#9733;'), ('5','&#9733; &#9733; &#9733; &#9733; &#9733; (very funny)')])

    q6 = RadioField('Joke 6', [validators.optional()], choices=[('1','&#9733; (not funny at all)'),
    ('2','&#9733; &#9733;'), ('3','&#9733; &#9733; &#9733; (somewhat funny)'),
    ('4','&#9733; &#9733; &#9733; &#9733;'), ('5','&#9733; &#9733; &#9733; &#9733; &#9733; (very funny)')])

    q7 = RadioField('Joke 7', [validators.optional()], choices=[('1','&#9733; (not funny at all)'),
    ('2','&#9733; &#9733;'), ('3','&#9733; &#9733; &#9733; (somewhat funny)'),
    ('4','&#9733; &#9733; &#9733; &#9733;'), ('5','&#9733; &#9733; &#9733; &#9733; &#9733; (very funny)')])

    q8 = RadioField('Joke 8', [validators.optional()], choices=[('1','&#9733; (not funny at all)'),
    ('2','&#9733; &#9733;'), ('3','&#9733; &#9733; &#9733; (somewhat funny)'),
    ('4','&#9733; &#9733; &#9733; &#9733;'), ('5','&#9733; &#9733; &#9733; &#9733; &#9733; (very funny)')])

    q9 = RadioField('Joke 9', [validators.optional()], choices=[('1','&#9733; (not funny at all)'),
    ('2','&#9733; &#9733;'), ('3','&#9733; &#9733; &#9733; (somewhat funny)'),
    ('4','&#9733; &#9733; &#9733; &#9733;'), ('5','&#9733; &#9733; &#9733; &#9733; &#9733; (very funny)')])

    q10 = RadioField('Joke 10', [validators.optional()], choices=[('1','&#9733; (not funny at all)'),
    ('2','&#9733; &#9733;'), ('3','&#9733; &#9733; &#9733; (somewhat funny)'),
    ('4','&#9733; &#9733; &#9733; &#9733;'), ('5','&#9733; &#9733; &#9733; &#9733; &#9733; (very funny)')])

    q11 = RadioField('Joke 11', [validators.optional()], choices=[('1','&#9733; (not funny at all)'),
    ('2','&#9733; &#9733;'), ('3','&#9733; &#9733; &#9733; (somewhat funny)'),
    ('4','&#9733; &#9733; &#9733; &#9733;'), ('5','&#9733; &#9733; &#9733; &#9733; &#9733; (very funny)')])

    q12 = RadioField('Joke 12', [validators.optional()], choices=[('1','&#9733; (not funny at all)'),
    ('2','&#9733; &#9733;'), ('3','&#9733; &#9733; &#9733; (somewhat funny)'),
    ('4','&#9733; &#9733; &#9733; &#9733;'), ('5','&#9733; &#9733; &#9733; &#9733; &#9733; (very funny)')])

    q13 = RadioField('Joke 13', [validators.optional()], choices=[('1','&#9733; (not funny at all)'),
    ('2','&#9733; &#9733;'), ('3','&#9733; &#9733; &#9733; (somewhat funny)'),
    ('4','&#9733; &#9733; &#9733; &#9733;'), ('5','&#9733; &#9733; &#9733; &#9733; &#9733; (very funny)')])

    q14 = RadioField('Joke 14', [validators.optional()], choices=[('1','&#9733; (not funny at all)'),
    ('2','&#9733; &#9733;'), ('3','&#9733; &#9733; &#9733; (somewhat funny)'),
    ('4','&#9733; &#9733; &#9733; &#9733;'), ('5','&#9733; &#9733; &#9733; &#9733; &#9733; (very funny)')])

    q15 = RadioField('Joke 15', [validators.optional()], choices=[('1','&#9733; (not funny at all)'),
    ('2','&#9733; &#9733;'), ('3','&#9733; &#9733; &#9733; (somewhat funny)'),
    ('4','&#9733; &#9733; &#9733; &#9733;'), ('5','&#9733; &#9733; &#9733; &#9733; &#9733; (very funny)')])
