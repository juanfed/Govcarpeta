#from govCarpeta.firebase import initFB, insertCitizens, readCitizens, readCitizenByIdAndName
from . import firebase
from . import utils
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponseRedirect
import os

def index(request):
    if request.method == 'GET':
        userName = request.session.get('userName')
        #userPassword = request.session.get('userPassword')
        userAddress = request.session.get('userAddress')
        userEmail = request.session.get('userEmail')
        FBState = request.session.get('FBState')
        userRegis = request.session.get('userRegis')
        userOperatorName = request.session.get('userOperatorName')
        
        return render(request, 'index.html', {
            'userName': userName,
            'userAddress': userAddress,
            'userEmail': userEmail,
            'FBState': FBState,
            'userRegis': userRegis,
            'userOperatorName': userOperatorName,
        })
    return render(request, 'index.html')

def registerCitizen(request):
    if request.method == 'POST':
        userID = request.session.get('userID')
        userName = request.session.get('userName')
        userAddress = request.session.get('userAddress')
        userEmail = request.session.get('userEmail')
        userPassword = request.session.get('userPassword')

        operatorId = request.POST.get('operatorId')
        operatorName = request.POST.get('operatorName')
        statusCode = utils.postRegisterCitizen(int(userID), userName, userAddress, userEmail, int(operatorId), operatorName)
        code = statusCode.split(',')[0]
        print(f'userID {userID}, userName {userName}, userAddress {userAddress}, userEmail {userEmail}, userPassword {userPassword}, operatorId {operatorId}, operatorName {operatorName}, ')
        print('code: ', code)
        if code == '201':
            statusCodeID = utils.validateCitizen(userID)
            codeID = statusCodeID.split(',')[0]
            print('codeID: ', codeID)
            if codeID == '200':
                FBstate = firebase.updateOperadorData(userID, userEmail, userPassword, operatorId, operatorName)
                if FBstate:
                    request.session['FBState'] = True 
                    firebase.updateisRegistered(userID, userEmail, userPassword)
                    return redirect('index')
                else:
                    request.session['FBState'] = False 
                    return redirect('index')
            else:
                request.session['FBState'] = False
                return redirect('index')
        #return HttpResponse("Form submitted successfully!")
    return render(request, 'swaggerCodes.html', {
        'statusCode': statusCode,
    })

def authenticateDocument(request):
    if request.method == 'POST':
        userName = request.session.get('userName')
        userAddress = request.session.get('userAddress')
        userEmail = request.session.get('userEmail')
        userPassword = request.session.get('userPassword')

        docID = request.POST.get('id')
        docURL = request.POST.get('url')
        docTitle = os.path.basename(docURL)
        statusCode = utils.authenticateDocument(docID, docURL, docTitle)
        code = statusCode.split(',')[0]
        #print(f'statusCode: {statusCode}')
        if code == '200':
            #print(f'docID: {docID}, docURL: {docURL}, docTitle: {docTitle}, userEmail: {userEmail}, userPassword: {userPassword}')
            FBstate = firebase.updatePath(docID, userEmail, userPassword, docURL)
            print(f'FBstate: {FBstate}')
            if FBstate:
                request.session['FBState'] = True 
                return redirect('index')
            else:
                request.session['FBState'] = False 
                return redirect('index')
        else:
            request.session['FBState'] = False
            return redirect('index')
    return render(request, 'swaggerCodes.html', {
        'statusCode': statusCode,
    })

def validateCitizen(request):
    if request.method == 'GET':
        id = request.GET.get('id')
        userEmail = request.session.get('userEmail')
        userPassword = request.session.get('userPassword')
        statusCode = utils.validateCitizen(id)
        code = statusCode.split(',')[0]
        if code == '200':
            FBstate = firebase.updateisRegistered(id, userEmail, userPassword)
            if FBstate:
                request.session['FBState'] = True 
                return redirect('index')
            else:
                request.session['FBState'] = False 
                return redirect('index')
        else:
            request.session['FBState'] = False
            return redirect('index')
    return render(request, 'swaggerCodes.html', {
        'statusCode': statusCode,
    })

def signUpCitizen(request):
    request.session.flush()
    if request.method == 'POST':
        id = request.POST.get('regisID')
        name = request.POST.get('regisUsername')
        address = request.POST.get('regisVic')
        email = request.POST.get('regisEmail')
        password = request.POST.get('regisPassword')
        operatorId = 0
        operatorName = 'null'
        # Insert data into Firebase
        firebase.insertCitizens(id, name, address, email, password, operatorId, operatorName)
        # Redirect to the login page with email parameter
        login_url = reverse('loginCitizen')
        return redirect(f'{login_url}')
    return render(request, 'login.html')

def loginCitizen(request):
    request.session.flush()
    if request.method == 'POST':
        email = request.POST.get('logInEmail')
        password = request.POST.get('logInPassword')
        userData = firebase.readCitizenByEmail(email, password)
        print(f'{email}, {password}')
        print(userData)
        if userData:
            first_register = userData[0]
            userID = first_register["data"]["id"]
            userName = first_register["data"]["name"]
            userAddress = first_register["data"]["address"]
            userPassword = first_register["data"]["password"]
            userRegis = first_register["data"]["isRegistered"]
            userOperatorName = first_register["data"]["operatorName"]
            # Store values in session
            request.session['userID'] = userID 
            request.session['userName'] = userName 
            request.session['userPassword'] = userPassword 
            request.session['userAddress'] = userAddress 
            request.session['userRegis'] = userRegis 
            request.session['userEmail'] = email 
            request.session['userOperatorName'] = userOperatorName 
            return redirect('index') 
        else:
            return render(request, 'login.html', {'invalid_credentials': True})
    return render(request, 'login.html')

def logoutUser(request):
    request.session.flush()
    return redirect('loginCitizen')