from django import forms

class UploadLeafForm(forms.Form):
    image = forms.ImageField(
        label="Leaf Image",
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
            'id': 'leafImageInput',
        })
    )
