from torchvision import transforms

# Single shared transform configuration standardized to 128x128 resolution
# with standard ImageNet normalization.
DISEASE_TRANSFORM = transforms.Compose([
    transforms.Resize((128, 128)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])
