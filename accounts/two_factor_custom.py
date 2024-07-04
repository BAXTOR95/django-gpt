from two_factor.views import SetupView
from two_factor.forms import TOTPDeviceForm


class CustomSetupView(SetupView):
    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form, **kwargs)
        if isinstance(form, TOTPDeviceForm):
            context['show_qr'] = True
        return context
