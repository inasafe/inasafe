#!/usr/bin/env bash
echo "🪛 Installing VSCode Extensions:"
echo "--------------------------------"
code --extensions-dir=.vscode-extensions --install-extension batisteo.vscode-django
code --extensions-dir=.vscode-extensions --install-extension donjayamanne.python-environment-manager
code --extensions-dir=.vscode-extensions --install-extension donjayamanne.python-extension-pack
code --extensions-dir=.vscode-extensions --install-extension github.copilot
code --extensions-dir=.vscode-extensions --install-extension github.copilot-chat
code --extensions-dir=.vscode-extensions --install-extension github.vscode-pull-request-github
code --extensions-dir=.vscode-extensions --install-extension hbenl.vscode-test-explorer
code --extensions-dir=.vscode-extensions --install-extension jamesqquick.python-class-generator
code --extensions-dir=.vscode-extensions --install-extension kevinrose.vsc-python-indent
code --extensions-dir=.vscode-extensions --install-extension littlefoxteam.vscode-python-test-adapter
code --extensions-dir=.vscode-extensions --install-extension ms-python.black-formatter
code --extensions-dir=.vscode-extensions --install-extension ms-python.debugpy
code --extensions-dir=.vscode-extensions --install-extension ms-python.python
code --extensions-dir=.vscode-extensions --install-extension ms-python.vscode-pylance
code --extensions-dir=.vscode-extensions --install-extension ms-vscode.test-adapter-converter
code --extensions-dir=.vscode-extensions --install-extension njpwerner.autodocstring
code --extensions-dir=.vscode-extensions --install-extension visualstudioexptteam.intellicode-api-usage-examples
code --extensions-dir=.vscode-extensions --install-extension visualstudioexptteam.vscodeintellicode
code --extensions-dir=.vscode-extensions --install-extension wholroyd.jinja

code --extensions-dir=".vscode-extensions" .
