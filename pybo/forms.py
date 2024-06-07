from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, SelectField, RadioField,DateField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, Email

class UserCreateForm(FlaskForm):
    username = StringField('사용자이름', validators=[DataRequired(), Length(min=3, max=25)])
    password1 = PasswordField('비밀번호', validators=[
        DataRequired(), EqualTo('password2', '비밀번호가 일치하지 않습니다')])
    password2 = PasswordField('비밀번호확인', validators=[DataRequired()])
    email = EmailField('이메일', validators=[DataRequired(), Email()])

class UserSchoolForm(FlaskForm):
    school = RadioField('학부', choices=[('인문사회대학'), ('경영대학'), ('생명보건대학'), ('AI/SW창의융합대학'), ('문화예술대학')], validators=[DataRequired()])


class UserMajorForm(FlaskForm):
    major = RadioField('학과', choices=[('전기전자공학과', '전기전자공학과'), ('스마트배터리학과', '스마트배터리학과'), ('드론로봇학과', '드론로봇학과'),
    ('철도건설공학과', '철도건설공학과'), ('컴퓨터공학과', '컴퓨터공학과'), ('소프트웨어학과', '소프트웨어학과'), ('정보보안학과', '정보보안학과'), ('게임공학과', '게임공학과')], validators=[DataRequired()])

class UserLoginForm(FlaskForm):
    username = StringField('사용자이름', validators=[DataRequired(), Length(min=3, max=25)])
    password = PasswordField('비밀번호', validators=[DataRequired()])

