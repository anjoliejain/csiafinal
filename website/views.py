from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, Response
from fpdf import FPDF
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_required, current_user
from .models import Note, Deals, TeamNotes, User
from . import db
import json
from sqlalchemy import delete
from datetime import *

views = Blueprint('views', __name__)

@views.route('/deals', methods=['GET', 'POST'])
def deals():
    if request.method == 'POST':
        DealID = request.form.get('dealid')
        DealName = request.form.get('dealName')
        ClientID = request.form.get('clientid')
        Comments = request.form.get('comments')
        DealStatus = request.form.get('dealstatus')
        Date = request.form.get('date')
        DateCreated = request.form.get('datecreated')

        new_deal = Deals(dealid = DealID, dealname = DealName, clientid = ClientID, comments = Comments, dealstatus = DealStatus, date = Date, datecreated = DateCreated)
        db.session.add(new_deal)
        db.session.commit()
        flash('Deal Added', category='success')

    our_deals=Deals.query.all()
    return render_template("deals.html", user=current_user, our_deals=our_deals)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        note = request.form.get('note')

        if len(note) < 1:
            flash('Note is too short!', category='error')
        else:
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Note added!', category='success')


    ongoing_deals = Deals.query.filter_by(dealstatus = "Ongoing").all()

    return render_template("home.html", user=current_user, ongoing_deals=ongoing_deals)


@views.route('/delete-note', methods=['POST'])
def delete_note():
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})


@views.route('/view-deals')
def viewdeals():
    all_data = Deals.query.all()
    return render_template('view-deals.html', user=current_user, deals=all_data)

@views.route('/view-employees')
def viewemployees():
    User.query.filter_by(id=3).delete()
    all_data = User.query.all()
    return render_template('view-users.html', user=current_user, employees=all_data)

@views.route('/view-notes')
def viewnotes():
    all_data = Note.query.all()
    return render_template('view-notes.html', user=current_user, notes=all_data)

@views.route('/delete/<dealid>/', methods = ['GET', 'POST'])
def delete(dealid):
    my_data = Deals.query.get(dealid)
    db.session.delete(my_data)
    db.session.commit()
    flash("Deal Deleted Successfully")
    return redirect(url_for('views.adminviewdeals'))

@views.route('/admindelete/<id>/', methods = ['GET', 'POST'])
def deleteuser(id):
    my_user = User.query.get(id)
    db.session.delete(my_user)
    db.session.commit()
    flash("User Deleted Successfully")
    return redirect(url_for('views.viewemployees'))

@views.route('/update', methods=['GET', 'POST'])
def update():
    if request.method == 'POST':
        my_data = Deals.query.get(request.form.get('dealid'))
        my_data.dealname = request.form['dealname']
        my_data.clientid = request.form['clientid']
        my_data.comments = request.form['comments']
        my_data.dealstatus = request.form.get('dealstatus')
        my_data.date = request.form['date']

        db.session.commit()
        flash("Deal Updated Successfully")
        return redirect(url_for('views.viewdeals'))

@views.route('/admin-home', methods=['GET', 'POST'])
def adminhome():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(
                password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            flash('Account created!', category='success')
            return redirect(url_for('views.viewemployees'))
    return render_template("adminhome.html", user=current_user)

@views.route('/download/alldealsreport/pdf')
def download_all_deals_report():
    result = Deals.query.all()
    pdf = FPDF()
    pdf.add_page()

    page_width = pdf.w - 2 * pdf.l_margin

    pdf.set_font('Times', 'B', 14.0)
    pdf.cell(page_width, 0.0, 'All Deals', align='C')
    pdf.ln(10)
    col_width = page_width / 7

    pdf.set_font('Times', 'B', 12)
    th = 15
    pdf.cell(col_width, th, 'Deal ID', border=1)
    pdf.cell(col_width, th, 'Deal Name', border=1)
    pdf.cell(col_width, th, 'Client ID', border=1)
    pdf.cell(col_width, th, 'Comments', border=1)
    pdf.cell(col_width, th, 'Deal Status', border=1)
    pdf.cell(col_width, th, 'Date Initiated', border=1)
    pdf.cell(col_width, th, 'Date Updated', border=1)
    pdf.ln(th)

    pdf.set_font('Times', '', 12)

    for row in result:
        pdf.cell(col_width, th, row.dealid, border=1)
        pdf.cell(col_width, th, row.dealname, border=1)
        pdf.cell(col_width, th, row.clientid, border=1)
        pdf.cell(col_width, th, row.comments, border=1)
        pdf.cell(col_width, th, row.dealstatus, border=1)
        pdf.cell(col_width, th, row.datecreated, border=1)
        pdf.cell(col_width, th, row.date, border=1)
        pdf.ln(th)

    pdf.ln(10)

    pdf.set_font('Times', '', 10.0)
    pdf.cell(page_width, 0.0, '- end of report -', align='C')

    return Response(pdf.output(dest='S').encode('latin-1'), mimetype='application/pdf',
                    headers={'Content-Disposition': 'attachment;filename=All Deals Report.pdf'})

@views.route('/download/ongoingdealsreport/pdf')
def download_ongoing_deals_report():
    result = Deals.query.filter_by(dealstatus = 'Ongoing').all()
    pdf = FPDF()
    pdf.add_page()

    page_width = pdf.w - 2 * pdf.l_margin

    pdf.set_font('Times', 'B', 14.0)
    pdf.cell(page_width, 0.0, 'Ongoing Deals', align='C')
    pdf.ln(10)
    col_width = page_width / 6

    pdf.set_font('Times', 'B', 12)
    th = 15
    pdf.cell(col_width, th, 'Deal ID', border=1)
    pdf.cell(col_width, th, 'Client ID', border=1)
    pdf.cell(col_width, th, 'Comments', border=1)
    pdf.cell(col_width, th, 'Deal Status', border=1)
    pdf.cell(col_width, th, 'Date', border=1)
    pdf.ln(th)

    pdf.set_font('Times', '', 12)

    for row in result:
        pdf.cell(col_width, th, row.dealid, border=1)
        pdf.cell(col_width, th, row.dealname, border=1)
        pdf.cell(col_width, th, row.clientid, border=1)
        pdf.cell(col_width, th, row.comments, border=1)
        pdf.cell(col_width, th, row.dealstatus, border=1)
        pdf.cell(col_width, th, row.date, border=1)
        pdf.ln(th)

    pdf.ln(10)

    pdf.set_font('Times', '', 10.0)
    pdf.cell(page_width, 0.0, '- end of report -', align='C')

    return Response(pdf.output(dest='S').encode('latin-1'), mimetype='application/pdf',
                    headers={'Content-Disposition': 'attachment;filename=Ongoing Deal Report.pdf'})

@views.route('/download/closeddealsreport/pdf')
def download_closed_deals_report():
    result = Deals.query.filter_by(dealstatus = 'Closed').all()
    pdf = FPDF()
    pdf.add_page()

    page_width = pdf.w - 2 * pdf.l_margin

    pdf.set_font('Times', 'B', 14.0)
    pdf.cell(page_width, 0.0, 'Closed Deals', align='C')
    pdf.ln(10)
    col_width = page_width / 6

    pdf.set_font('Times', 'B', 12)
    th = 15
    pdf.cell(col_width, th, 'Deal ID', border=1)
    pdf.cell(col_width, th, 'Deal Name', border=1)
    pdf.cell(col_width, th, 'Client ID', border=1)
    pdf.cell(col_width, th, 'Comments', border=1)
    pdf.cell(col_width, th, 'Deal Status', border=1)
    pdf.cell(col_width, th, 'Date', border=1)
    pdf.ln(th)

    pdf.set_font('Times', '', 12)

    for row in result:
        pdf.cell(col_width, th, row.dealid, border=1)
        pdf.cell(col_width, th, row.dealname, border=1)
        pdf.cell(col_width, th, row.clientid, border=1)
        pdf.cell(col_width, th, row.comments, border=1)
        pdf.cell(col_width, th, row.dealstatus, border=1)
        pdf.cell(col_width, th, row.date, border=1)
        pdf.ln(th)

    pdf.ln(10)

    pdf.set_font('Times', '', 10.0)
    pdf.cell(page_width, 0.0, '- end of report -', align='C')

    return Response(pdf.output(dest='S').encode('latin-1'), mimetype='application/pdf',
                    headers={'Content-Disposition': 'attachment;filename=Closed Deals Report.pdf'})


@views.route('/dealinterface/<dealid>/', methods=['GET', 'POST'])
def deal_progress(dealid):
    if request.method == 'POST':
        Name = request.form.get('name')
        Update = request.form.get('update')
        new_update = TeamNotes(name=current_user.first_name, update=Update, deal_id=dealid)
        db.session.add(new_update)
        db.session.commit()
        flash('Note added!', category='success')

    all_notes = TeamNotes.query.filter_by(deal_id=dealid).all()

    return render_template("dealinterface.html", user=current_user, all_notes=all_notes)


@views.route('/deletenote/<noteid>/', methods = ['GET', 'POST'])
def delete_update(noteid):
    note_data = TeamNotes.query.get(noteid)
    db.session.delete(note_data)
    db.session.commit()
    flash("Note Deleted Successfully")
    return redirect(url_for('views.viewdeals'))

@views.route('/admin-viewdeals')
def adminviewdeals():
    all_data = Deals.query.all()
    return render_template('admin-viewdeals.html', user=current_user, deals=all_data)

@views.route('/admin-dealinterface/<dealid>/', methods=['GET', 'POST'])
def admindealinterface(dealid):
    all_notes = TeamNotes.query.filter_by(deal_id=dealid).all()
    return render_template("admin-dealinterface.html", user=current_user, all_notes=all_notes)

@views.route('/admin-deletenote/<noteid>/', methods = ['GET', 'POST'])
def admin_delete_update(noteid):
    note_data = TeamNotes.query.get(noteid)
    db.session.delete(note_data)
    db.session.commit()
    flash("Note Deleted Successfully")
    return redirect(url_for('views.adminviewdeals'))