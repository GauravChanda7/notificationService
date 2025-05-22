'use strict'

const messageTypeComponent = document.querySelector('#message-type');
const addFieldComponent = document.querySelector('#add-field');
const formComponent = document.querySelector('#form');

function renderFields(){
    messageTypeComponent.addEventListener('click', handleInputSelection);
}

function handleInputSelection(event) {
    let target = event.target;

    addFieldComponent.innerHTML = '';
    const existingSubmit = document.querySelector('#submit');
    if (existingSubmit) {
        existingSubmit.remove();
    }

    let recipientInputHTML = '';
    let submitValue = '';

    switch (target.id) {
        case 'email-btn':
            recipientInputHTML = `<input type="email" name="recpmail" id="recpmail" placeholder="Recipient E-Mail">`;
            submitValue = 'Submit Email';
            break;
        case 'message-btn':
            recipientInputHTML = `<input type="text" name="recpnum" id="recpnum" placeholder="Recipient Phone Number (add countrycode)">`;
            submitValue = 'Submit Message';
            break;
        case 'inapp-btn':
            recipientInputHTML = `<input type="text" name="recpname" id="recpname" placeholder="Recipient User Name">`;
            submitValue = 'Submit Notification';
            break;
        default:
            return;
    }

    addFieldComponent.innerHTML = recipientInputHTML;

    const submitBtn = document.createElement('input');
    submitBtn.type = 'submit';
    submitBtn.name = 'action';
    submitBtn.value = submitValue;
    submitBtn.id = 'submit';

    formComponent.appendChild(submitBtn);
}

renderFields();
