# Sway named workspaces handler

This script is a full drop-in replacement for workspace switching and naming.
In vanilla sway renamed workspaces cannot be renamed, rearranged, swapped
between displays, or navigated between without many `swaymsg rename` commands
that are annoying to type in. This script automates these commands and will
maintain the workspaces' numeric sequence, plus allow dmenu navigation to a
space when you have many. Does not use i3ipc.

## Features
 - Rename and rearrange workspaces without having to think
 - mod+num bindings always work
 - Move windows between spaces
 - Move containers to other workspaces
 - Create new workspaces with a randomized name
 - Basic support for multiple outputs
 - Python scripts can be edited in place
 - Structured git-style command line options via Typer

## Cons / notes / not-tested things / todo
 - Notes / big cons
    - It sends a long list of `swaymsg rename` commands every time but I have not noticed any speed issues.
    - Mostly usable in a console, but it simply reruns the init functions every time you do something.
    - Does not use `i3ipc`, it is completely stateless when run by sway.
    - My setup is 2 displays and I have not tested with more, but I think it should work
    - Will not play well with your existing numbered workspaces, works best on a cold boot
 - Small stuff
    - Needs function for moving current window to other output, current way is to use `container send`
    - Prevent collisions with new random names
    - Default workspace at init is not renamed
 - Big stuff
    - Monolithic `SwaySpaces` object will need to be split up when more output controls are added
    - Adding config and logging
    - Select between alternatives to dmenu which I do not use
    - Consider geometry when moving between displays, currently it just reads in order from `swaymsg -t get_inputs`
 - Things that would be nice
    - More lists of random workspace names
    - Remember workspace outputs
    - Option to keep cursor on current display when switching outputs, may be configurable with cursor warp in sway
    - `tmux-resurrect` style recovery

## Python dependencies
 - Boxes.py
 - dmenu-python
 - Typer


## Usage in sway config

Example bindings:

```
set $py "your-python-path"
set $swayctl "path-to-swayctl.py"

bindcode $m+34           exec $py $swayctl workspace focus left # brackets
bindcode $m+35           exec $py $swayctl workspace focus right
bindcode $m+Control+34   exec $py $swayctl workspace move left
bindcode $m+Control+35   exec $py $swayctl workspace move right
bindsym $m+Shift+o       exec $py $swayctl workspace move next_output
bindsym $m+n             exec $py $swayctl workspace new
bindsym $m+Control+r     exec $py $swayctl workspace rename
bindsym $m+g             exec $py $swayctl workspace go
bindsym $m+m             exec $py $swayctl container send
bindcode $m+Shift+34     exec $py $swayctl container move left
bindcode $m+Shift+35     exec $py $swayctl container move right
bindsym $m+o             exec $py $swayctl output next
bindcode $m+49           exec $py $swayctl output next # tilde
bindsym $m+1             exec $py $swayctl workspace number 1
bindsym $m+2             exec $py $swayctl workspace number 2
bindsym $m+3             exec $py $swayctl workspace number 3
bindsym $m+4             exec $py $swayctl workspace number 4
bindsym $m+5             exec $py $swayctl workspace number 5
bindsym $m+6             exec $py $swayctl workspace number 6
bindsym $m+7             exec $py $swayctl workspace number 7
bindsym $m+8             exec $py $swayctl workspace number 8
bindsym $m+9             exec $py $swayctl workspace number 9
bindsym $m+0             exec $py $swayctl workspace number 10

# Recommended
bar {
    strip_workspace_numbers yes 
    }
```

