from time import perf_counter
import torch
from diffusers import StableDiffusionXLPipeline, EulerDiscreteScheduler
from huggingface_hub import hf_hub_download

queue = []

# Food
queue.extend([{
  'prompt': 'food photography, cheesecake, blueberries and jam, cinnamon, in a luxurious Michelin kitchen style, depth of field, ultra detailed, natural features',
  'seed': 78934567,
}])

# Portrait
queue.extend([{
  'prompt': 'close up, woman, headdress, neon iridescent tattoos, snow forest, intricate, 8k, cinematic lighting, volumetric lighting, 8k',
  'seed': 55986344589,
}])

# Animal
queue.extend([{
  'prompt': 'a fish made out of dendrobium flowers, ultrarealistic, highly detailed, 8k',
  'seed': 501798843,
}])

# Macro
queue.extend([{
  'prompt': 'macro photography of beautiful nails with manicure, painting, oil paints, gold splashes, professional color palette',
  'seed': 1963386471,
}])

# Text
queue.extend([{
  'prompt': 'video game room with a big neon sign that says "arcade", cinematic, 8k, natural lighting, HDR, high resolution, shot on IMAX Laser',
  'seed': 1138562738,
}])

# 3D
queue.extend([{
  'prompt': '3d isometric dungeon game',
  'seed': 3812179903,
}])

# Download model from https://civitai.com/models/133005?modelVersionId=348913
pipe = StableDiffusionXLPipeline.from_single_file(
  r'D:\juggernautXL_v9Rundiffusionphoto2.safetensors',
  use_safetensors=True,
  local_files_only=True,
  torch_dtype=torch.float16,
).to('cuda')

pipe.load_lora_weights(hf_hub_download('ByteDance/SDXL-Lightning', 'sdxl_lightning_4step_lora.safetensors'))
pipe.fuse_lora()

pipe.scheduler = EulerDiscreteScheduler.from_config(
  pipe.scheduler.config,
  timestep_spacing='trailing',
)

generator = torch.Generator(device='cuda')

# warm up
for generation in queue[:3]:
  pipe(generation['prompt'])

for i, generation in enumerate(queue, start=1):
  image_start = perf_counter()

  generator.manual_seed(generation['seed'])

  image = pipe(
    prompt=generation['prompt'],
    guidance_scale=0.0,
    num_inference_steps=4,
    generator=generator,
  ).images[0]

  image.save(f'image_{i}.png')

  generation['total_time'] = perf_counter() - image_start

images_totals = ', '.join(map(lambda generation: str(round(generation['total_time'], 1)), queue))
print('Image time:', images_totals)

images_average = round(sum(generation['total_time'] for generation in queue) / len(queue), 1)
print('Average image time:', images_average)

max_memory = round(torch.cuda.max_memory_allocated(device='cuda') / 1000000000, 2)
print('Max. memory used:', max_memory, 'GB')
