# wx_sweetpapers

## Dependencies

- Python
- swww (<https://github.com/LGFae/swww>)

## Description

Automatically sets multiple monitors to pre-determined 'packs' of wallpapers

`wx_sweetpapers` includes 3 Components

1. [Wallpaper Swapper](#wallpaper-swapper)
2. [Chrome Extension](#chrome-extension)
3. [HTTP Wallpaper Download Daemon](#http-wallpaper-download-daemon)
4. [Wofi Menu](#wofi-menu)

### Components

#### Wallpaper Swapper

Rotates between `packs` of wallpapers, randomly picking wallpapers
from these packs and painting them to the respective monitors.

#### Chrome Extension

Tries to find an element on the current active tab with the class `WX_ACTIVEIMAGE`,
and retrieve its `src`, if it cannot find an element like this, it uses
the active tabs URL as the images `src`. It then transmits the image
to the HTTP Download Daemon

#### HTTP Wallpaper Download Daemon

Basically, chrome extensions cannot automatically save to the file system,
they can 'download' using the browser API, or save to the browser storage.
But they cannot read or modify the base file system.

To get around this, we spin up a service that listens to HTTP requests
from the Chrome Extension. The chrome extension retrieves the image from
the active tab, and transmits it to the Download Daemon,
the download daemon then automatically names the image according to the
required schema `<monitor>_<index>.<extension>` i.e. `1.png, 1_2.png, 1_3.png, etc`
for the main Wallpaper Swapper to use

#### Wofi Menu

Allows for quick swapping between wallpaper packs

![Wofi Menu](assets/wofi_menu.png "Wofi Menu")

## TODO

- [ ] Convert HTTP-Daemon to Go?

## Settings

### Arguments

- `-c --config`: the configuration file to use
- `-p --profile`: the actual 'pack' to use.

`i.e.  sweetpapers.py -c sweetpapers.json -p Background1`
Will swap between `Background1/Oceans` and `Background1/Mountains`
picking random images each time

```example

- sweetpapers.jsonc
- Wallpapers
  |- Background1
    |- Oceans
      |- 1.jpg
      |- 2.jpg
    |- Mountains
      |- 1.jpg
      |- 2.jpg
      |- 2_1.jpg

```

### Configuration

#### Example Configuration

```jsonc
{
  "screens": {
    "1": {
      "name": "DP-3",
      "orientation": "landscape",
    },
    "2": {
      "name": "HDMI-A-1",
      "orientation": "portrait",
    },
    "3": {
      "name": "DP-2",
      "orientation": "portrait",
    },
  },
  "defaults": {
    "auto": false,
    "debug": true,
    "sequence": false,
    "packs_location": "~/Wallpapers/packs",
  },
  "transition": {
    "next": "ordered",
    "fill_mode": "crop",
    "interval": 5,
    "transition_type": "fade",
    "transition_duration": 2,
    "transition_step": 20,
    "transition_fps": 255,
  },
}
```

- `defaults.random`: whether naming schema is followed or not,
  if true, will automatically paint portrait images to portrait screens and horizontal
  to horizontal screens (based on `screens.[id].orientation`) otherwise will paint
  images based on their path prefix id (_1_.jpg, _2_.jpg) to `screens.[id].name`

- `defaults.sequence`: if true, will swap a single screen and wait for `transition.interval`
  before swapping next if false, will swap all monitors at the same time, then wait
  `transition.interval` before swapping all monitors again

- `defaults.packs_location`: the root pack, Main loop iterates over
  `defaults.packs_location/(--profile)` directories. See: [Arguments](#arguments)

- `transition.next`: (random, ordered), random will randomly select a directory to
  switch to each loop, ordered will go through alphabetically
- `transition.interval`: amount of time (seconds) between switching
- `transition.transition_*`: See: [man swww-daemon](https://github.com/LGFae/swww/blob/main/doc/swww-img.1.scd)
