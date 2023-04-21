from flask import Flask, Response, render_template, request, redirect, url_for
from connect import * 
import time

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/choosevm')
def chooseVm():
    return render_template('chooseVm.html')


@app.route('/vminfo')
def vmInfo():
    vm = request.args['vm']
    return render_template('vmInfo.html', vm=vm)

@app.route('/azure')
def azure():
    vm_value = request.args.get('vm')
    if vm_value == 'other':
        return redirect(url_for('chooseVm', vm = vm_value))
    if vm_value == 'windows' or vm_value == 'linux':
        return redirect(url_for('vmInfo', vm = vm_value))
    return redirect(url_for('home'))


@app.route('/create-<vm>-vm')
async def createVm(vm):
    return Response(await create_vm_async(vm), mimetype='text/html')


@app.route('/destroy-machine', methods=['POST'])
def deleteVm():
    response = deleteRessources()
    if "error" in response:
        return "Error destroying machine", 500
    else:
        return "Machine destroyed successfully"
        

if (__name__ == '__main__'):
    app.run(debug=True)