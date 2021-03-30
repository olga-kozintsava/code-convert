import docx2txt
import json

import os
import pathlib
import subprocess

from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.template.loader import get_template
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.generic import FormView, TemplateView, ListView
from base.forms import RegistrationForm, InputTextForm, LoginForm, DeleteConvertForm, UploadFileForm
from base.models import Convert, Account, ConvertTransaction
from base.token import account_activation_token

User = get_user_model()



class RegistrationView(TemplateView):
    template_name = 'signup.html'

    def get(self, request, *args, **kwargs):
        signup_form = RegistrationForm(self.request.GET, prefix='signup_form')
        login_form = LoginForm(self.request.GET, prefix='login_form')
        context = self.get_context_data(**kwargs)
        context['signup_form'] = signup_form
        context['login_form'] = login_form
        return render(request, self.template_name, context)

    def post(self, request):
        action = self.request.POST['action']
        if action == 'signup':
            signup_form = RegistrationForm(data=request.POST, prefix='signup_form')
            if signup_form.is_valid():
                user = signup_form.save(commit=False)
                user.is_active = False
                user.save()
                current_site = get_current_site(request)
                email = signup_form.cleaned_data['email']
                template = get_template('email.html')
                email_message = f'Welcome to code convert'
                send_mail(
                    subject='Activate your account',
                    message=email_message,
                    html_message=template.render(context={
                        'user': user,
                        'domain': current_site.domain,
                        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                        'token': account_activation_token.make_token(user),
                    }),
                    from_email='Code convert',
                    recipient_list=[email]
                )
                return JsonResponse({"status": 200})
            else:
                return JsonResponse({"errors": json.dumps(signup_form.errors)}, status=400)
        elif action == 'login':
            login_form = LoginForm(data=request.POST, prefix='login_form')
            if login_form.is_valid():
                user = authenticate(
                    self.request,
                    username=login_form.cleaned_data['username'],
                    password=login_form.cleaned_data['password']
                )
                if user is not None:
                    if user.is_active:
                        login(self.request, user)
                        return JsonResponse({"status": 200})
                    else:
                        return JsonResponse({"error": "Disabled account"}, status=403)
                else:
                    return JsonResponse({"error": "invalid login or password"}, status=400)
            else:
                return JsonResponse({"error": json.dumps(login_form.errors)}, status=400)


class ConfirmRegistration(TemplateView):
    template_name = 'confirm_registration.html'


class UserHistoryView(LoginRequiredMixin, ListView):
    model = Convert
    template_name = 'history.html'
    context_object_name = 'user_convert'
    paginate_by = settings.PAGE_SIZE

    def get_queryset(self, *args):
        user_convert = Convert.objects.filter(id_user=self.request.user.id)
        return user_convert


class DownloadView(FormView):
    template_name = 'history.html'
    http_method_names = ['post']
    form_class = DeleteConvertForm

    def form_valid(self, form):
        action = self.request.POST['action']
        convert_id = form.cleaned_data['convert_id']
        convert_item = get_object_or_404(Convert, id=convert_id)
        if convert_item:
            if action == 'download_input':
                file_path = convert_item.in_file
                if os.path.exists(file_path):
                    with open(file_path, 'rb') as fp:
                        response = HttpResponse(fp.read(), content_type='text/plain')
                        if 'open_input' in self.request.POST:
                            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
                            return response
                        elif 'download_input' in self.request.POST:
                            response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(file_path)
                            return response
                raise Http404
            if action == 'download_output':
                file_path = convert_item.out_file
                if os.path.exists(file_path):
                    with open(file_path, 'rb', ) as fp:
                        response = HttpResponse(fp.read(), content_type='text/plain')
                        if 'open_output' in self.request.POST:
                            response['Content-Disposition'] = 'inline; filename=Result_' + os.path.basename(file_path)
                            return response
                        elif 'download_output' in self.request.POST:
                            response['Content-Disposition'] = 'attachment; filename=Result_' + os.path.basename(
                                file_path)
                            return response
                raise Http404
        return super().form_valid(form)

    def get_success_url(self):
        return self.request.META.get('HTTP_REFERER') \
               or reverse_lazy('history')


class InputView(LoginRequiredMixin, TemplateView):
    template_name = 'start.html'

    def get(self, request, *args, **kwargs):
        text_form = InputTextForm(self.request.GET, prefix='text_form')
        file_form = UploadFileForm(self.request.GET, prefix='file_form')
        context = self.get_context_data(**kwargs)
        context['text_form'] = text_form
        context['file_form'] = file_form
        return render(request, self.template_name, context)


class DeleteConvertView(FormView):
    template_name = 'history.html'
    http_method_names = ['post']
    form_class = DeleteConvertForm

    def form_valid(self, form):
        convert_id = form.cleaned_data['convert_id']
        convert_item = Convert.objects.filter(
            id=convert_id
        )
        if convert_item:
            convert_item.delete()
        return super().form_valid(form)

    def get_success_url(self):
        return self.request.META.get('HTTP_REFERER') \
               or reverse_lazy('history')


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return render(request, 'confirm_registration.html')

    else:
        return HttpResponse('Activation link is invalid!')


def ajax_open_file(request):
    convert_id = request.GET.get('id')
    type_response = request.GET.get('type')
    convert_item = get_object_or_404(Convert, id=convert_id)
    file_path = convert_item.out_file
    if os.path.exists(file_path):
        with open(file_path, 'r') as fp:
            response = HttpResponse(fp.read(), content_type='text/plain')
            if type_response == 'd':
                response['Content-Disposition'] = 'attachment;filename=Result_' + os.path.basename(file_path)
            elif type_response == 'o':
                response['Content-Disposition'] = 'inline;filename=Result_' + os.path.basename(file_path)
        return response


def ajax_upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            upload_file = form.cleaned_data['file']
            word_type = ['application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                         'application/msword']
            name = request.user.username
            date = timezone.now()
            date_format = date.strftime('%Y%m%d%H%M%S')
            p = pathlib.Path(f'{settings.INPUT_PATH}/{name}/')
            p.mkdir(parents=True, exist_ok=True)
            file_name = f'{name}_{date_format}.txt'
            input_path = p / file_name
            file_type = upload_file.content_type
            if file_type in word_type:
                input_text = docx2txt.process(upload_file)
                with open(input_path, "w") as text_file:
                    text_file.write(input_text)
            else:
                with open(input_path, 'wb+') as text_file:
                    for chunk in upload_file.chunks():
                        text_file.write(chunk)
            file = open(input_path, 'rb').read()
            loc = len(file)
            size = upload_file.size
            user_acc = get_object_or_404(Account, user=request.user)
            if loc > user_acc.balance:
                return JsonResponse({"error": "You don’t have enough points"}, status=403)
            elif loc < user_acc.balance:
                return JsonResponse(
                    {"len": loc,
                     "file_path": str(input_path),
                     "size": size,
                     "date": date,
                     "file_name": file_name
                     },
                    status=200)
            else:
                return JsonResponse({"error": "invalid file"}, status=415)


def convert_upload_file(request):
    if request.method == 'POST':
        response_data = {}
        data = request.POST
        loc = int(data['len'])
        input_path = data['file_path']
        new_convert = Convert(
            id_user=request.user,
            in_file=input_path,
            in_file_loc=loc,
            in_file_size=data['size'],
            in_tmstmp=data['date'])
        new_convert.save()
        cmd = f'python3 engine.py -dir={input_path}'
        cmd_split = cmd.split()
        process = subprocess.Popen(cmd_split, stdout=subprocess.PIPE)
        output, errors = process.communicate()
        output_decode = output.decode("utf-8").split('\n')
        convert_id = new_convert.id
        to_update = get_object_or_404(Convert, id=convert_id)
        name = request.user.username
        file_name = data['file']
        p = pathlib.Path(f'{settings.INPUT_PATH}/{name}/')
        out_path = f'{p}/Results/{file_name}'
        to_update.out_file = out_path
        # to_update.out_tmstmp = datetime.datetime.strptime(output_decode[2], '%Y-%m-%d %H:%M:%S.%f')
        to_update.out_tmstmp = timezone.now()
        to_update.save()
        new_transaction = ConvertTransaction(
            account=request.user.balance,
            amount=loc,
            date=timezone.now(),
            id_convert_id=new_convert.id
        )
        new_transaction.save()
        response_data['id'] = convert_id
        response_data['status'] = ' success'

        return JsonResponse(response_data)
    else:
        return JsonResponse({"error": "File upload error"}, status=403)


def ajax_input_text(request):
    if request.method == 'POST':
        form = InputTextForm(data=request.POST)
        if form.is_valid():
            text_input = form.cleaned_data['text_input']
            loc = int(request.POST['text_len'])
            name = request.user.username
            date = timezone.now()
            date_format = date.strftime('%Y%m%d%H%M%S')
            p = pathlib.Path(f'{settings.INPUT_PATH}/{name}/')
            p.mkdir(parents=True, exist_ok=True)
            file_name = f'{name}_{date_format}.txt'
            input_path = p / file_name
            input_path.write_text(text_input, encoding="utf-8")
            size = os.stat(input_path).st_size
            new_convert = Convert(
                id_user=request.user,
                in_file=input_path,
                in_file_loc=loc,
                in_file_size=size,
                in_tmstmp=date
            )
            new_convert.save()
            cmd = f'python3 engine.py -dir={input_path}'
            cmd_split = cmd.split()
            process = subprocess.Popen(cmd_split, stdout=subprocess.PIPE)
            output, errors = process.communicate()
            output_decode = output.decode("utf-8").split('\n')
            to_update = get_object_or_404(Convert, id=new_convert.id)
            out_path = f'{p}/Results/{file_name}'
            to_update.out_tmstmp = timezone.now()
            to_update.out_file = out_path
            # to_update.out_tmstmp = datetime.datetime.strptime(output_decode[2], '%Y-%m-%d %H:%M:%S.%f')
            to_update.save()
            new_transaction = ConvertTransaction(
                account=request.user.balance,
                amount=loc,
                date=timezone.now(),
                id_convert_id=new_convert.id
            )
            new_transaction.save()
            with open(out_path, 'r') as f:
                convert_data = f.read()
                response = HttpResponse(convert_data, content_type='text/plain')
                response['Content-Disposition'] = 'inline; filename=Result_' + os.path.basename(out_path)
                response['id'] = new_convert.id
                return response
        else:
            JsonResponse({"error": "Input text error"}, status=403)


def check_len(request):
    if request.method == 'GET':
        text_len = request.GET.get('len')
        user_acc = get_object_or_404(Account, user=request.user)
        if int(text_len) > user_acc.balance:
            return JsonResponse({"error": "Please top up balance"}, status=403)
        else:
            return JsonResponse({"status": 200})
