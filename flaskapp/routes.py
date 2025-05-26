from flask import render_template, flash, redirect, url_for, request
from flaskapp import app, db
from flaskapp.models import BlogPost, IpView, Day, UkData
from flaskapp.forms import PostForm
import datetime

import pandas as pd
import json
import plotly
import plotly.express as px


# Route for the home page, which is where the blog posts will be shown
@app.route("/")
@app.route("/home")
def home():
    # Querying all blog posts from the database
    posts = BlogPost.query.all()
    return render_template('home.html', posts=posts)


# Route for the about page
@app.route("/about")
def about():
    return render_template('about.html', title='About page')


# Route to where users add posts (needs to accept get and post requests)
@app.route("/post/new", methods=['GET', 'POST'])
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = BlogPost(title=form.title.data, content=form.content.data, user_id=1)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Post', form=form)


# Route to the dashboard page
@app.route('/dashboard')
def dashboard():
    days = Day.query.all()
    df = pd.DataFrame([{'Date': day.id, 'Page views': day.views} for day in days])

    fig = px.bar(df, x='Date', y='Page views')

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('dashboard.html', title='Page views per day', graphJSON=graphJSON)


@app.before_request
def before_request_func():
    day_id = datetime.date.today()  # get our day_id
    client_ip = request.remote_addr  # get the ip address of where the client request came from

    query = Day.query.filter_by(id=day_id)  # try to get the row associated to the current day
    if query.count() > 0:
        # the current day is already in table, simply increment its views
        current_day = query.first()
        current_day.views += 1
    else:
        # the current day does not exist, it's the first view for the day.
        current_day = Day(id=day_id, views=1)
        db.session.add(current_day)  # insert a new day into the day table

    query = IpView.query.filter_by(ip=client_ip, date_id=day_id)
    if query.count() == 0:  # check if it's the first time a viewer from this ip address is viewing the website
        ip_view = IpView(ip=client_ip, date_id=day_id)
        db.session.add(ip_view)  # insert into the ip_view table

    db.session.commit()  # commit all the changes to the database

@app.route('/dashboard_2')
def dashboard_2():
    uk_data = UkData.query.all()
    uk_df = pd.DataFrame([
    {
        'Constituency': uk.constituency_name,
        'Voter Turnout in 2019': uk.Turnout19,
        'c11FulltimeStudent': uk.c11FulltimeStudent,
        'c11Retired': uk.c11Retired,
        'c11Female': uk.c11Female,
        'c11HouseOwned': uk.c11HouseOwned
    }
    for uk in uk_data
    ])

    # Get 10 constituencies with the lowest turnout
    lowest_turnout = uk_df.nsmallest(10, 'Voter Turnout in 2019')
    
    # Plot only those 10
    fig1 = px.bar(
        lowest_turnout,
        x='Constituency',
        y='Voter Turnout in 2019',
        title='10 Constituencies with the Lowest Voter Turnout (2019)',
        labels={'Voter Turnout in 2019': 'Turnout (%)'}
    )
    fig1.update_layout(xaxis_tickangle=-45)  # Rotate x-axis labels for readability

    # Chart 2: Grouped bar for demographic averages
    demographics = ['FulltimeStudent', 'Retired', 'Women', 'HouseOwned']
    summary = lowest_turnout[demographics].mean().reset_index()
    summary.columns = ['Demographic', 'Average %']

    fig2 = px.bar(
        summary,
        x='Demographic',
        y='Average %',
        title='Average Demographics in Lowest Turnout Constituencies'
    )

    # Encode both plots
    graphJSON1 = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)
    graphJSON2 = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template(
        'dashboard2.html',
        title='Low Turnout Analysis',
        graphJSON1=graphJSON1,
        graphJSON2=graphJSON2
    )

    
