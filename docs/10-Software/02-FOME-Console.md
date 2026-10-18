# ECU Console

ECU Console is the Capoworks Java/Swing frontend supplied with a matching firmware build. It provides a serial or simulator connection, raw console messages, bench-test controls, a Lua editor and an engine-sniffer view. The inherited `fome_console` name is a technical artifact name; it is not evidence that an upstream or separately branded package is compatible. This page documents source behavior and makes no stable-release or universal-artifact promise.

## Launch and platform

Use the console from the same Capoworks build and board target as the firmware and TunerStudio INI. See the [firmware update guide](/Intro-Start-Here/HT-Updating-The-Firmware) for artifact and flashing workflow.

To build from source, start with a fully initialized checkout and submodules, including `java_console/luaformatter`. From the project root on POSIX:

```sh
cd java_tools
./gradlew :ui:shadowJar
```

On Windows:

```bat
cd java_tools
.\gradlew.bat :ui:shadowJar
```

The Gradle root is `java_tools`. The UI shadow task writes into `${rootDir}/../java_console_binary`, names the archive `fome_console`, and removes the version classifier, producing `java_console_binary/fome_console.jar` at the source project root. From that project root, launch it directly with:

```sh
java -jar java_console_binary/fome_console.jar
```

On Windows, use `java -jar java_console_binary\fome_console.jar` or the matching packaged `fome_console.exe`. The Launch4j configuration declares Java 21 as its minimum runtime. These are source-build and launch instructions, not a claim that a prebuilt package exists for every platform; launch an executable or JAR from the matching package rather than mixing files between packages.

The UI entry point is
[`Launcher.java`](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/java_console/ui/src/main/java/com/rusefi/Launcher.java#L50).
The [Gradle UI shadow task](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/java_console/ui/build.gradle#L22) sets the output directory, base name, and classifier at lines 23-25. The [Gradle project layout](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/java_tools/settings.gradle#L23) includes `ui` and `luaformatter` at lines 23-26, and the [Gradle wrapper distribution](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/java_tools/gradle/wrapper/gradle-wrapper.properties#L3) selects Gradle 9.3.0 at line 3. The [Windows Launch4j configuration](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/misc/console_launcher/fome_console.xml#L17) creates `fome_console.exe` and sets its minimum Java version to 21 at line 21.

## Connection

With no port argument, the console scans serial ports and checks for real Capoworks hardware and bootloader states. It also checks the local simulator at `localhost:29001`, as defined in [`TcpConnector.java`](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/java_console/io/src/main/java/com/rusefi/io/tcp/TcpConnector.java#L20). The startup screen enables **Connect** only for recognized ECU ports. An OpenBLT port is shown as bootloader mode and should be used through the firmware-update path, not a normal connection. These checks are in
[`StartupFrame.java`](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/java_console/ui/src/main/java/com/rusefi/StartupFrame.java#L181)
and
[`SerialPortScanner.java`](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/java_console/ui/src/main/java/com/rusefi/SerialPortScanner.java#L108).

Before connecting, the frontend compares the controller signature bundle with the console bundle. A mismatch produces a warning and can be cancelled; continuing is explicitly at the user's risk. After connection, the main window reports firmware and signature information and reads the configuration.

## Main tabs and utilities

The current UI opens four tabs:

- **Messages** accepts raw text commands and displays firmware responses.
- **Bench Test** exposes fan, A/C relay, fuel pump, spark, injector, MIL, idle, starter, reboot and DFU controls.
- **Lua Scripting** reads, formats, writes and resets the stored script, and can burn configuration.
- **Engine Sniffer** displays trigger, injection, ignition and related trace channels.

The tabs are created in
[`ConsoleUI.java`](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/java_console/ui/src/main/java/com/rusefi/ConsoleUI.java#L50);
the startup screen's simulator action is implemented in [`SimulatorHelper.java`](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/java_console/ui/src/main/java/com/rusefi/SimulatorHelper.java#L60).
Bench-test controls send firmware text commands; for example, the spark control constructs a `sparkbench2 ...` command and the fuel-pump control sends `fuelpumpbench`
([`BenchTestPane.java`](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/java_console/ui/src/main/java/com/rusefi/BenchTestPane.java#L95)).
The Lua **Reset/Reload** action sends `luareset`, while writing the script uses the binary configuration protocol.

The console also has command-line developer utilities such as `help`, `send_command`, `reboot_ecu` and `reboot_dfu` in
[`ConsoleTools.java`](https://github.com/capoworks/capoworks-ecu/blob/bf0d5a7dc445fb7e4ebf9dd8a059c6e9a991cbd3/java_console/ui/src/main/java/com/rusefi/tools/ConsoleTools.java#L24).
These are frontend entry points, not a complete public CLI contract. A GUI button label is likewise not a firmware command; the text token actually sent is the command.

## Troubleshooting

- If no serial port appears, check the cable and ECU power. The startup source specifically prompts the user to confirm that the blue LED is blinking.
- If a bootloader or DFU device is reported, use **Update Firmware** and follow the [flashing guide](/Software/Flashing-Software-Notes).
- If the bundle or signature warning appears, stop and obtain the console, firmware and INI from the same Capoworks build.
- If connection fails after port selection with a compatibility message, treat it as a firmware/console definition mismatch first.
- If **Start Virtual Simulator** reports port `29001` busy, an existing simulator may still be running.

Bench tests can command real outputs. Confirm the test environment and connected hardware before using them.
