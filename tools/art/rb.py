import sys
from rembg import remove, new_session
from PIL import Image
I, O = sys.argv[1], sys.argv[2]
for model in ['isnet-general-use']:
    s = new_session(model)
    for n in ['1.webp','2.jpg','3.jpg','4.jpg','5.jpg']:
        im = Image.open(f'{I}/{n}').convert('RGB')
        out = remove(im, session=s, post_process_mask=True)
        out.save(f'{O}/{n.split(".")[0]}_{model}.png'); print(n, im.size)
