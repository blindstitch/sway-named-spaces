from sway import SwaySpaces, sm
import typer
import dmenu

s = SwaySpaces()

app = typer.Typer()

workspace_commands = typer.Typer()
app.add_typer(workspace_commands, name="workspace")

container_commands = typer.Typer()
app.add_typer(container_commands, name="container")

output_commands = typer.Typer()
app.add_typer(output_commands, name="output")


# Workspaces

@workspace_commands.command("move")
def workspace_move(direction):
    s.move_workspace(direction)

@workspace_commands.command("focus")
def workspace_focus(direction):
    sm("workspace "+s.focused(direction).name)

@workspace_commands.command("rename")
def workspace_rename():
    s.rename(dmenu.show(['']))

@workspace_commands.command("new")
def workspace_new():
    s.new()

@workspace_commands.command("go")
def workspace_go():
    s.go(dmenu.show(s.spaces(key='basename')))

@workspace_commands.command("number")
def workspace_number(num:int):
    if num > len(s.spaces('current')):
        s.new()
    else:
        s.go(s.spaces('current')[num-1].basename)



# Containers

@container_commands.command("send")
def container_send():
    dest = s.find(dmenu.show(s.spaces(key='basename'))).name
    command = f"move container to workspace {dest}"
    print(command)
    sm(command)

@container_commands.command("move")
def container_move(direction):
    match direction:
        case 'next_output':
            # start_output = name of starting monitor
            # sm(f"focus output "+dest_output)
            # dest_ws = 
            # focus back to starting monitor
            # move container to that workspace
            # sm(f"move container to workspace {dest_ws}")
            # 
            pass
        case other:
            sm(f"move container to workspace {s.focused(direction).name}")
            sm(f"workspace {s.focused(direction).name}")


@output_commands.command("next")
def output_next(): sm(f"focus output {s.output(1)}")
@output_commands.command("prev")
def output_prev(): sm(f"focus output {s.output(-1)}")



if __name__ == "__main__":
    app()
