from django import forms
from .models import CrawlRequest, ParameterHandler, ResponseHandler



class CrawlRequestForm(forms.ModelForm):
    class Meta:
        model = CrawlRequest

        labels = {
            'request_type': 'Request method',
        }

        fields = [
            'source_name',
            'base_url',
            'request_type',
            'obey_robots',
            'captcha',

            'antiblock_download_delay',
            'antiblock_autothrottle_enabled',
            'antiblock_autothrottle_start_delay',
            'antiblock_autothrottle_max_delay',
            'antiblock_mask_type',
            'antiblock_ip_rotation_type',
            'antiblock_max_reqs_per_ip',
            'antiblock_max_reuse_rounds',
            'antiblock_proxy_list',
            'antiblock_reqs_per_user_agent',
            'antiblock_user_agents_file',
            'antiblock_cookies_file',
            'antiblock_persist_cookies',

            'has_webdriver',
            'webdriver_path',
            'img_xpath',
            'sound_xpath',
            'crawler_type',
            'explore_links',
            'link_extractor_max_depth',
            'link_extractor_allow',
            'link_extractor_allow_extensions',
        ]


class RawCrawlRequestForm(CrawlRequestForm):
    # BASIC INFO ##############################################################

    source_name = forms.CharField(label="Source Name", max_length=200,
        widget=forms.TextInput(attrs={'placeholder': 'Example'})
    )
    base_url = forms.CharField(label="Base URL", max_length=200,
        widget=forms.TextInput(attrs={
            'placeholder': 'www.example.com/data/',
            'onchange': 'detailBaseUrl();'
        })
    )
    obey_robots = forms.BooleanField(required=False, label="Obey robots.txt")

    # ANTIBLOCK ###############################################################

    # Options for Delay
    antiblock_download_delay = forms.IntegerField(
        required=False,
        label="Average delay in Seconds (or min delay if autothrottle is on).",
        initial=2,
    )
    antiblock_autothrottle_enabled = forms.BooleanField(
        required=False,
        label="Enable autothrottle",

        widget=forms.CheckboxInput(
            attrs={
                "onclick": "autothrottleEnabled();",
            }
        )
    )
    antiblock_autothrottle_start_delay = forms.IntegerField(
        required=False,
        label="Starting delay",
        initial=2,
    )
    antiblock_autothrottle_max_delay = forms.IntegerField(
        required=False,
        label="Max delay",
        initial=10,
    )

    # Options for mask type
    antiblock_mask_type = forms.ChoiceField(
        required=False, choices=(
            ('none', 'None'),
            # ('ip', 'IP rotation'),
            # ('user_agent', 'User-agent rotation'),
            # ('delay', 'Delays'),
            # ('cookies', 'Use cookies'),
        ),
        widget=forms.Select(attrs={'onchange': 'detailAntiblock();'})
    )

    # Options for IP rotation
    antiblock_ip_rotation_type = forms.ChoiceField(
        required=False, choices=(
            ('tor', 'Tor'),
            ('proxy', 'Proxy'),
        ),
        widget=forms.Select(attrs={'onchange': 'detailIpRotationType();'})
    )
    antiblock_proxy_list = forms.CharField(
        required=False, max_length=2000, label="Proxy List",
        widget=forms.TextInput(attrs={
            'placeholder': 'Paste here the content of your proxy list file'
        })
    )
    antiblock_max_reqs_per_ip = forms.IntegerField(
        required=False,
        label="Max Requisitions per IP",
        initial=10,
    )
    antiblock_max_reuse_rounds = forms.IntegerField(
        required=False,
        label="Max Reuse Rounds",
        initial=10,
    )

    # Options for User Agent rotation
    antiblock_reqs_per_user_agent = forms.IntegerField(required=False,
        label="Requests per User Agent")
    antiblock_user_agents_file = forms.CharField(
        required=False, max_length=2000, label="User Agents File",
        widget=forms.TextInput(attrs={
            'placeholder': 'Paste here the content of your user agents file'
        })
    )

    # Options for Cookies
    antiblock_cookies_file = forms.CharField(
        required=False, max_length=2000, label="Cookies File",
        widget=forms.TextInput(attrs={
            'placeholder': 'Paste here the content of your cookies file'
        })
    )
    antiblock_persist_cookies = forms.BooleanField(required=False,
        label="Persist Cookies")

    # CAPTCHA #################################################################
    captcha = forms.ChoiceField(
        choices=(
            ('none', 'None'),
            ('image', 'Image'),
            ('sound', 'Sound'),
        ),
        widget=forms.Select(attrs={'onchange': 'detailCaptcha();'})
    )
    # Options for Captcha
    has_webdriver = forms.BooleanField(
        required=False, label="Use webdriver",
        widget = forms.CheckboxInput(attrs={
            'onchange': 'detailWebdriverType(); defineValid("captcha")'
        })
    )
    webdriver_path = forms.CharField(
        required=False, max_length=2000, label="Download directory",
        widget=forms.TextInput(attrs={
            'placeholder': 'Download directory path'
        })
    )
    img_xpath = forms.CharField(
        required=False, label="Image Xpath", max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Image Xpath'})
    )
    sound_xpath = forms.CharField(
        required=False, label="Sound Xpath", max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Sound Xpath'})
    )

    # CRAWLER TYPE ############################################################
    crawler_type = forms.ChoiceField(
        required=False, choices=(
            ('static_page', 'Static Page'),
            # ('form_page', 'Page with Form'),
            # ('single_file', 'Single File'),
            # ('bundle_file', 'Bundle File'),
        ),
        widget=forms.Select(attrs={'onchange': 'detailCrawlerType();'})
    )
    explore_links = forms.BooleanField(required=False, label="Explore links")

    # Crawler Type - Static
    link_extractor_max_depth = forms.IntegerField(
        required=False, label="Link extractor max depth (blank to not limit):"
    )
    link_extractor_allow = forms.CharField(
        required=False, max_length=2000,
        label="Allow urls that match with the regex (blank to not filter):",
        widget=forms.TextInput(attrs={
            'placeholder': 'Regex for allowing urls'
        })
    )
    link_extractor_allow_extensions = forms.CharField(
        required=False, max_length=2000,
        label="List of allowed extensions (comma separed):",
        widget=forms.TextInput(attrs={'placeholder': 'pdf,xml'})
    )
    # Crawler Type - Page with form
    # Crawler Type - Single file
    # Crawler Type - Bundle file


class ResponseHandlerForm(forms.ModelForm):
    """
    Contains the fields related to the configuration of a single step in the
    response validation mechanism
    """
    class Meta:
        model = ResponseHandler
        exclude = []
        widgets = {
            'handler_type': forms.Select(attrs=
                {
                    'onchange': 'detailTemplatedUrlResponseParams(event);'
                }
            ),
        }


class ParameterHandlerForm(forms.ModelForm):
    """
    Contains the fields related to the configuration of the request parameters
    to be injected
    """

    class Meta:
        model = ParameterHandler
        fields = '__all__'
        labels = {
            'first_num_param': 'First value to generate:',
            'last_num_param': 'Last value to generate:',
            'step_num_param': 'Step size:',
            'leading_num_param': 'Leading zeros?',
            'length_alpha_param': 'Word length:',
            'num_words_alpha_param': 'Number of words:',
            'no_upper_alpha_param': 'Lowercase only?',
            'date_format_date_param': 'Date format to use:',
            'start_date_date_param': 'Starting date:',
            'end_date_date_param': 'End date:',
            'frequency_date_param': 'Frequency to generate',
        }

        widgets = {
            'parameter_type': forms.Select(attrs={
                'onchange': 'detailTemplatedUrlParamType(event);'
            }),
            'date_format_date_param': forms.TextInput(attrs={
                'placeholder': '%m/%d/%Y'
            }),
        }


# Formset for ResponseHandler forms
ResponseHandlerFormSet = forms.inlineformset_factory(CrawlRequest,
    ResponseHandler, form=ResponseHandlerForm, exclude=[], extra=1, min_num=0,
    can_delete=True)


# Formset for ParameterHandler forms
ParameterHandlerFormSet = forms.inlineformset_factory(CrawlRequest,
    ParameterHandler, form=ParameterHandlerForm, exclude=[], extra=1, min_num=0,
    can_delete=True)
