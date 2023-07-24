[Setup]
AppName=SubwayTkinter
AppVersion=1.2
DefaultDirName={pf}\SubwayTkinter
DefaultGroupName=SubwayTkinter
OutputDir=dist\

[Files]
Source: "/Users/coke/PycharmProjects/subscribe-subway/subway*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs

[Icons]
Name: "{app.}\Your Application"; Filename: "{app}\YourApp.exe"
