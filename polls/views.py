from django.http import HttpResponse,HttpResponseRedirect
from .models import Question,Answer #isRelatedTo
from django.shortcuts import render,get_object_or_404, redirect
from django.urls import reverse
import operator
from nltk.corpus import stopwords 
from django.conf import settings
import random
from random import choice
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .forms import UserForm
from collections import OrderedDict
from statistics import mean
from django.db import connection


def index(request):

    submitbutton = request.POST.get('submit')
    nextQuestion = request.POST.get('nextQuestion')
    answer = request.POST.get('answer')
    model = settings.WORD2VEC

    print("username:", request.user.username)
    cursor = connection.cursor()
    cursor.execute('select count(*) as total from auth_user;')
    numOfUsers= Answer.objects.raw("select count(*) as total from auth_user;")
    row = cursor.fetchone()
    numOfUsers = row[0]

    #not logged in
    if not request.user.is_authenticated:
        return render(request, 'polls/login.html', {})
    
    #first time logged in
    if  request.session.get('question_id') is None:
        print ('First time logged in')
        q= Question.objects.raw("select * from polls_question where id not in (select question_id from polls_answer,auth_user where user_id=auth_user.id and auth_user.username='"+request.user.username+"');")
        list=[]
        for p in q:
            list.append(p.id)

        if list == []:
            messages.error(request,'You have already replied all the questions!')
            return logout_view(request)
        
        rnd = random.choice(list)
        print (rnd)
        print (list)
        latest_question = Question.objects.get(pk=rnd)
        request.session['question_id']=rnd
        list.remove(rnd)
        request.session['remaining_questions']=list
        print (list)
    elif nextQuestion is not None:
        print("Clicked next question")
        list = request.session['remaining_questions']
        if list == []:   
            request.session.flush()
            logout(request)
            return logout_view(request)
        rnd = choice([i for i in list if i not in [request.session['question_id']]])
        print (rnd)
        list.remove(rnd)
        latest_question = Question.objects.get(pk=rnd)
        request.session['question_id']=rnd
        request.session['remaining_questions']=list
    else:
        latest_question = Question.objects.get(pk=request.session['question_id'])

    if request.session.get("score") is None:
        request.session["score"]=0

    if request.session.get("list_of_answers") is None:
        request.session["list_of_answers"]=OrderedDict()
    
    scores={}
    list_of_answers=OrderedDict()
    print(answer)
    if answer is not None:
        if len(request.session['list_of_answers']) == 14:
            messages.info(request, 'No more answers needed! Click the next question button to continue...')
            context = {
                'latest_question': latest_question,
                'answer': answer,
                'closest_item': None,
                'score': request.session['score'],
                'list_of_answers': request.session['list_of_answers'] }
            return render(request, 'polls/index.html', context)

        scores = check_similarity(answer, model, latest_question)
        sortedItems = sorted(scores.items(), key=operator.itemgetter(1))
        print(sortedItems)
        closest_item = sortedItems[len(sortedItems)-1][0]

        if len(sortedItems)==0:
            closest_item = None
            score = 0
        else:
            filteredItems= []
            for item in sortedItems:
                if item[1]>=0.8:
                    filteredItems.append(item)
            print(filteredItems)
            
            if (len(filteredItems)==0):
                score=0
            else:
                flat_list = [sublist[1] for sublist in filteredItems]
                meanScore = sum(flat_list) / len(flat_list)
                score = int(round((len(filteredItems)/numOfUsers)*100*meanScore))
                print(len(filteredItems)/numOfUsers)
                print((len(filteredItems)/numOfUsers)*100*meanScore)
                print(score)

        if request.session['list_of_answers'] is None:
            list_of_answers[answer]=score
        else:
            list_of_answers=request.session['list_of_answers']
            list_of_answers[answer]=score     
        request.session['list_of_answers'] = list_of_answers
        score = request.session['score'] + score
        request.session['score'] = score

        print(request.user)        
        saved_answer = Answer(question = latest_question, user = request.user, answer_text = answer, answer_order = len(request.session['list_of_answers']), votes = 0, score = score)
        saved_answer.save()
    elif nextQuestion is not None:
        closest_item=None
        score=request.session['score']
        list_of_answers=OrderedDict()
        request.session['list_of_answers']=OrderedDict()
    else:
        closest_item=None
        score=request.session['score']
        list_of_answers=request.session['list_of_answers']
    
    context = {
        'latest_question': latest_question,
        'answer': answer,
        'closest_item': closest_item,
        'score': score,
        'list_of_answers': list_of_answers
    }
    return render(request, 'polls/index.html', context)

def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/detail.html', {'question': question})

def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/results.html', {'question': question})

def logout_view(request):
    lboard= Answer.objects.raw("select auth_user.id, username, sum(score) as total from polls_answer, auth_user where auth_user.id=polls_answer.user_id group by user_id order by total desc;")
    leaderboard=OrderedDict()
    for l in lboard:
        leaderboard[l.username]=l.total

    context = {
        'leaderboard': leaderboard,
    }
    print(leaderboard)
    request.session.flush()
    logout(request)
    return render(request, 'polls/logout.html', context)

def login_view(request):

    if request.POST.get('newAccount') is not None:
        return render(request, 'polls/register.html')

    if request.POST.get('login') is not None:
        print("The user clicked login")

        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            print("The user is authenticated")
            login(request,user)
            return redirect('polls:index')
        else:
            print("Someone tried to login and failed.")
            print("They used username: {} and password: {}".format(username,password))
            messages.error(request,'Username or password not correct')
            return render(request, 'polls/login.html')
    else:
        return render(request, 'polls/login.html')
    

def check_similarity(sentence, model, question):
    stops = set(stopwords.words("english"))
    check_sentence = [w for w in sentence.lower().split() if not w in stops]
    doc = question.answer_set.all()
    scores = dict()
    for line in doc:
        print(line)
        line=str(line)
         #line = line[0:len(line)-1]#I think this is needed for escaping '\n'
        words = [w for w in line.lower().split() if not w in stops]
        try:
            scores[line] = model.n_similarity(words, check_sentence)
        except Exception:
            scores=dict()

    return scores


def register(request):
    if request.POST.get('register') is not None:
        user_form = UserForm(data=request.POST)
        if user_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            return redirect('polls:index')
        else:
            print(user_form.errors)
    else:
        user_form = UserForm()

    return render(request,'polls/register.html',
                          {'user_form':user_form})



# def q2(request):
#     answer = request.POST.get('answer')
#     model = settings.WORD2VEC
#     newQuestion = request.POST.get('newQuestion')


#     if newQuestion is not None:
#         try:
#             previous_answers = Answer.objects.all().filter(question=request.session['question_id'],user=request.session['username'])[request.session['index'] + 1]
#             print(previous_answers)
#             latest_question = Question.objects.get(pk=request.session['q2'])
#             latest_question.question_text=latest_question.question_text.replace('following','\"'+previous_answers.answer_text+'\"')
#             request.session['index'] =  request.session['index'] + 1
#         except IndexError as e:
#             context = {
#                 'latest_question': None,
#                 'answer': None,
#                 'closest_item': None,
#                 'score': request.session['score'],
#                 'list_of_answers': None,
#             }
#             return render(request, 'polls/q3.html', context)
        
        

#     print ("request.session['question_id']", request.session['question_id'])
#     if request.session.get("q2") is None:
#         isRel = isRelatedTo.objects.get(question1=request.session['question_id'])
#         q2 = isRel.getRelatedQuestion2()
#         #q3 = isRel.getRelatedQuestion3()
#         request.session['index'] = 0
#         request.session['list_of_answers'] = None
#         request.session["q2"]=q2.id
#         #request.session["q3"]=q3.id
    

#     previous_answers = Answer.objects.all().filter(question=request.session['question_id'],user=2)[request.session['index']]
#     print(previous_answers)
                
#     latest_question = Question.objects.get(pk=request.session['q2'])
#     latest_question.question_text=latest_question.question_text.replace('following','\"'+previous_answers.answer_text+'\"')
#         # q=latest_question.question_text
#         # for prev_answer in previous_answers:
#         #     q.replace("following", prev_answer)
#         #     q.replace("events", 'event')


#     if answer is not None:

#         scores = check_similarity(answer, model, latest_question)
#         sortedItems = sorted(scores.items(), key=operator.itemgetter(1))
#         print(sortedItems)
#         closest_item = sortedItems[len(sortedItems)-1][0]
#         score = int(sortedItems[len(sortedItems)-1][1]*100)
#         if request.session['list_of_answers'] is None:
#             list_of_answers[answer]=score
#         else:
#             list_of_answers=request.session['list_of_answers']
#             list_of_answers[answer]=score     
#         request.session['list_of_answers'] = list_of_answers
#         score = request.session['score'] + score
#         request.session['score'] = score
#     else:
#         closest_item=None
#         score=request.session['score']
#         list_of_answers=request.session['list_of_answers']
    
#     context = {
#         'latest_question': latest_question,
#         'answer': answer,
#         'closest_item': closest_item,
#         'score': score,
#         'list_of_answers': list_of_answers,
#         'previous_answers': previous_answers 
#     }
    
#     return render(request, 'polls/q2.html', context)


# def q3(request):
#     return render(request, 'polls/q3.html', context)   


