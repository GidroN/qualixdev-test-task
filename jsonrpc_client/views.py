import json
import logging

from django.conf import settings
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import FormView

from .forms import InputForm
from .utils import process_rpc_request

logger = logging.getLogger('jsonrpc_client.views')


class InputFormView(FormView):
    template_name = 'jsonrpc_client/index.html'
    form_class = InputForm
    success_url = reverse_lazy('main')

    def form_valid(self, form):
        method = form.cleaned_data['method']
        params = form.cleaned_data['parameters']

        try:
            params = json.loads(params)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON: {e}")
            form.add_error('parameters', "Invalid JSON format")
            return self.form_invalid(form)

        url = settings.API_URL
        key = settings.CLIENT_KEY
        certificate = settings.CLIENT_CERTIFICATE

        response, error = process_rpc_request(url, key, certificate, method, params)
        if error:
            logger.error(f"Error during JSON-RPC call: {error}")
            form.add_error(None, error)
            return self.form_invalid(form)

        pretty_response = json.dumps(response, indent=4, ensure_ascii=False)
        return render(self.request, self.template_name,
                      {
                          "form": form,
                          "result": pretty_response
                      })
