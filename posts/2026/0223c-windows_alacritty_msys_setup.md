## Alacritty, MSYS setup on Windows

install msys2 and alacritty

create `C:\Users\[UID]\AppData\Roaming\alacritty\alacritty.toml` with below contents

```
[general]
import = ["alacritty-theme/themes/gruvbox_dark.toml",]
working_directory = "C:\\msys64\\home\\[UID]"

[env]
TERM = "xterm-256color"

[font]
normal = { family = "Consolas", style = "Regular" }
size = 12.00

[terminal]
#shell = "powershell"
shell = "C:\\msys64\\usr\\bin\\bash.exe"

[keyboard]
bindings = [
    { key = "N", mods = "Alt", action = "CreateNewWindow" },
    { key = "Q", mods = "Alt", action = "Quit" },
]
```

update `C:\msys64\home\[UID]\.profile` file with below contents

```bash
# Set user-defined locale
export LANG=$(locale -uU)

# if running bash
if [ -n "${BASH_VERSION}" ]; then
  if [ -f "${HOME}/.bashrc" ]; then
    source "${HOME}/.bashrc"
  fi
fi
```

update `C:\msys64\home\[UID]\.bashrc` file with below contents

```bash
# If not running interactively, don't do anything
[[ "$-" != *i* ]] && return

# set PATH environment variable and bash prompt (PS1)
export PATH=/bin:$PATH
export PS1="\[\e[32m\]\u@\h:\[\e[33m\]\w\$ "
```
