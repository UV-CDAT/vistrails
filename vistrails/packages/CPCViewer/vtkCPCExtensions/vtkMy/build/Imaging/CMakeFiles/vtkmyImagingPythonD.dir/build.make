# CMAKE generated file: DO NOT EDIT!
# Generated by "Unix Makefiles" Generator, CMake Version 2.8

#=============================================================================
# Special targets provided by cmake.

# Disable implicit rules so canonical targets will work.
.SUFFIXES:

# Remove some rules from gmake that .SUFFIXES does not remove.
SUFFIXES =

.SUFFIXES: .hpux_make_needs_suffix_list

# Suppress display of executed commands.
$(VERBOSE).SILENT:

# A target that is always out of date.
cmake_force:
.PHONY : cmake_force

#=============================================================================
# Set environment variables for the build.

# The shell in which to execute make rules.
SHELL = /bin/sh

# The CMake executable.
CMAKE_COMMAND = "/Applications/CMake 2.8-12.app/Contents/bin/cmake"

# The command to remove a file.
RM = "/Applications/CMake 2.8-12.app/Contents/bin/cmake" -E remove -f

# Escaping for special characters.
EQUALS = =

# The program to use to edit the cache.
CMAKE_EDIT_COMMAND = "/Applications/CMake 2.8-12.app/Contents/bin/ccmake"

# The top-level source directory on which CMake was run.
CMAKE_SOURCE_DIR = /Developer/Projects/EclipseWorkspace/vistrails/vistrails/packages/CPCViewer/vtkCPCExtensions/vtkMy

# The top-level build directory on which CMake was run.
CMAKE_BINARY_DIR = /Developer/Projects/EclipseWorkspace/vistrails/vistrails/packages/CPCViewer/vtkCPCExtensions/build

# Include any dependencies generated for this target.
include Imaging/CMakeFiles/vtkmyImagingPythonD.dir/depend.make

# Include the progress variables for this target.
include Imaging/CMakeFiles/vtkmyImagingPythonD.dir/progress.make

# Include the compile flags for this target's objects.
include Imaging/CMakeFiles/vtkmyImagingPythonD.dir/flags.make

Imaging/vtkImageFooPython.cxx: /Developer/Projects/EclipseWorkspace/uvcdat/devel/install/build/ParaView-build/bin/vtkWrapPython-pv4.1
Imaging/vtkImageFooPython.cxx: /Developer/Projects/EclipseWorkspace/vistrails/vistrails/packages/CPCViewer/vtkCPCExtensions/vtkMy/Wrapping/hints
Imaging/vtkImageFooPython.cxx: /Developer/Projects/EclipseWorkspace/vistrails/vistrails/packages/CPCViewer/vtkCPCExtensions/vtkMy/Imaging/vtkImageFoo.h
Imaging/vtkImageFooPython.cxx: Imaging/vtkmyImagingPython.args
	$(CMAKE_COMMAND) -E cmake_progress_report /Developer/Projects/EclipseWorkspace/vistrails/vistrails/packages/CPCViewer/vtkCPCExtensions/build/CMakeFiles $(CMAKE_PROGRESS_1)
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --blue --bold "Python Wrapping - generating vtkImageFooPython.cxx"
	cd /Developer/Projects/EclipseWorkspace/vistrails/vistrails/packages/CPCViewer/vtkCPCExtensions/build/Imaging && /Developer/Projects/EclipseWorkspace/uvcdat/devel/install/build/ParaView-build/bin/vtkWrapPython-pv4.1 @/Developer/Projects/EclipseWorkspace/vistrails/vistrails/packages/CPCViewer/vtkCPCExtensions/build/Imaging/vtkmyImagingPython.args -o /Developer/Projects/EclipseWorkspace/vistrails/vistrails/packages/CPCViewer/vtkCPCExtensions/build/Imaging/vtkImageFooPython.cxx /Developer/Projects/EclipseWorkspace/vistrails/vistrails/packages/CPCViewer/vtkCPCExtensions/vtkMy/Imaging/vtkImageFoo.h

Imaging/vtkmyImagingPythonInit.cxx: /Developer/Projects/EclipseWorkspace/uvcdat/devel/install/build/ParaView-build/bin/vtkWrapPythonInit-pv4.1
Imaging/vtkmyImagingPythonInit.cxx: Imaging/vtkmyImagingPythonInit.data
	$(CMAKE_COMMAND) -E cmake_progress_report /Developer/Projects/EclipseWorkspace/vistrails/vistrails/packages/CPCViewer/vtkCPCExtensions/build/CMakeFiles $(CMAKE_PROGRESS_2)
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --blue --bold "Python Wrapping - generating vtkmyImagingPythonInit.cxx"
	cd /Developer/Projects/EclipseWorkspace/vistrails/vistrails/packages/CPCViewer/vtkCPCExtensions/build/Imaging && /Developer/Projects/EclipseWorkspace/uvcdat/devel/install/build/ParaView-build/bin/vtkWrapPythonInit-pv4.1 /Developer/Projects/EclipseWorkspace/vistrails/vistrails/packages/CPCViewer/vtkCPCExtensions/build/Imaging/vtkmyImagingPythonInit.data /Developer/Projects/EclipseWorkspace/vistrails/vistrails/packages/CPCViewer/vtkCPCExtensions/build/Imaging/vtkmyImagingPythonInit.cxx /Developer/Projects/EclipseWorkspace/vistrails/vistrails/packages/CPCViewer/vtkCPCExtensions/build/Imaging/vtkmyImagingPythonInitImpl.cxx

Imaging/vtkmyImagingPythonInitImpl.cxx: Imaging/vtkmyImagingPythonInit.cxx

Imaging/CMakeFiles/vtkmyImagingPythonD.dir/vtkImageFooPython.cxx.o: Imaging/CMakeFiles/vtkmyImagingPythonD.dir/flags.make
Imaging/CMakeFiles/vtkmyImagingPythonD.dir/vtkImageFooPython.cxx.o: Imaging/vtkImageFooPython.cxx
	$(CMAKE_COMMAND) -E cmake_progress_report /Developer/Projects/EclipseWorkspace/vistrails/vistrails/packages/CPCViewer/vtkCPCExtensions/build/CMakeFiles $(CMAKE_PROGRESS_3)
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Building CXX object Imaging/CMakeFiles/vtkmyImagingPythonD.dir/vtkImageFooPython.cxx.o"
	cd /Developer/Projects/EclipseWorkspace/vistrails/vistrails/packages/CPCViewer/vtkCPCExtensions/build/Imaging && /usr/bin/c++   $(CXX_DEFINES) $(CXX_FLAGS) -o CMakeFiles/vtkmyImagingPythonD.dir/vtkImageFooPython.cxx.o -c /Developer/Projects/EclipseWorkspace/vistrails/vistrails/packages/CPCViewer/vtkCPCExtensions/build/Imaging/vtkImageFooPython.cxx

Imaging/CMakeFiles/vtkmyImagingPythonD.dir/vtkImageFooPython.cxx.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/vtkmyImagingPythonD.dir/vtkImageFooPython.cxx.i"
	cd /Developer/Projects/EclipseWorkspace/vistrails/vistrails/packages/CPCViewer/vtkCPCExtensions/build/Imaging && /usr/bin/c++  $(CXX_DEFINES) $(CXX_FLAGS) -E /Developer/Projects/EclipseWorkspace/vistrails/vistrails/packages/CPCViewer/vtkCPCExtensions/build/Imaging/vtkImageFooPython.cxx > CMakeFiles/vtkmyImagingPythonD.dir/vtkImageFooPython.cxx.i

Imaging/CMakeFiles/vtkmyImagingPythonD.dir/vtkImageFooPython.cxx.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/vtkmyImagingPythonD.dir/vtkImageFooPython.cxx.s"
	cd /Developer/Projects/EclipseWorkspace/vistrails/vistrails/packages/CPCViewer/vtkCPCExtensions/build/Imaging && /usr/bin/c++  $(CXX_DEFINES) $(CXX_FLAGS) -S /Developer/Projects/EclipseWorkspace/vistrails/vistrails/packages/CPCViewer/vtkCPCExtensions/build/Imaging/vtkImageFooPython.cxx -o CMakeFiles/vtkmyImagingPythonD.dir/vtkImageFooPython.cxx.s

Imaging/CMakeFiles/vtkmyImagingPythonD.dir/vtkImageFooPython.cxx.o.requires:
.PHONY : Imaging/CMakeFiles/vtkmyImagingPythonD.dir/vtkImageFooPython.cxx.o.requires

Imaging/CMakeFiles/vtkmyImagingPythonD.dir/vtkImageFooPython.cxx.o.provides: Imaging/CMakeFiles/vtkmyImagingPythonD.dir/vtkImageFooPython.cxx.o.requires
	$(MAKE) -f Imaging/CMakeFiles/vtkmyImagingPythonD.dir/build.make Imaging/CMakeFiles/vtkmyImagingPythonD.dir/vtkImageFooPython.cxx.o.provides.build
.PHONY : Imaging/CMakeFiles/vtkmyImagingPythonD.dir/vtkImageFooPython.cxx.o.provides

Imaging/CMakeFiles/vtkmyImagingPythonD.dir/vtkImageFooPython.cxx.o.provides.build: Imaging/CMakeFiles/vtkmyImagingPythonD.dir/vtkImageFooPython.cxx.o

Imaging/CMakeFiles/vtkmyImagingPythonD.dir/vtkmyImagingPythonInitImpl.cxx.o: Imaging/CMakeFiles/vtkmyImagingPythonD.dir/flags.make
Imaging/CMakeFiles/vtkmyImagingPythonD.dir/vtkmyImagingPythonInitImpl.cxx.o: Imaging/vtkmyImagingPythonInitImpl.cxx
	$(CMAKE_COMMAND) -E cmake_progress_report /Developer/Projects/EclipseWorkspace/vistrails/vistrails/packages/CPCViewer/vtkCPCExtensions/build/CMakeFiles $(CMAKE_PROGRESS_4)
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Building CXX object Imaging/CMakeFiles/vtkmyImagingPythonD.dir/vtkmyImagingPythonInitImpl.cxx.o"
	cd /Developer/Projects/EclipseWorkspace/vistrails/vistrails/packages/CPCViewer/vtkCPCExtensions/build/Imaging && /usr/bin/c++   $(CXX_DEFINES) $(CXX_FLAGS) -o CMakeFiles/vtkmyImagingPythonD.dir/vtkmyImagingPythonInitImpl.cxx.o -c /Developer/Projects/EclipseWorkspace/vistrails/vistrails/packages/CPCViewer/vtkCPCExtensions/build/Imaging/vtkmyImagingPythonInitImpl.cxx

Imaging/CMakeFiles/vtkmyImagingPythonD.dir/vtkmyImagingPythonInitImpl.cxx.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/vtkmyImagingPythonD.dir/vtkmyImagingPythonInitImpl.cxx.i"
	cd /Developer/Projects/EclipseWorkspace/vistrails/vistrails/packages/CPCViewer/vtkCPCExtensions/build/Imaging && /usr/bin/c++  $(CXX_DEFINES) $(CXX_FLAGS) -E /Developer/Projects/EclipseWorkspace/vistrails/vistrails/packages/CPCViewer/vtkCPCExtensions/build/Imaging/vtkmyImagingPythonInitImpl.cxx > CMakeFiles/vtkmyImagingPythonD.dir/vtkmyImagingPythonInitImpl.cxx.i

Imaging/CMakeFiles/vtkmyImagingPythonD.dir/vtkmyImagingPythonInitImpl.cxx.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/vtkmyImagingPythonD.dir/vtkmyImagingPythonInitImpl.cxx.s"
	cd /Developer/Projects/EclipseWorkspace/vistrails/vistrails/packages/CPCViewer/vtkCPCExtensions/build/Imaging && /usr/bin/c++  $(CXX_DEFINES) $(CXX_FLAGS) -S /Developer/Projects/EclipseWorkspace/vistrails/vistrails/packages/CPCViewer/vtkCPCExtensions/build/Imaging/vtkmyImagingPythonInitImpl.cxx -o CMakeFiles/vtkmyImagingPythonD.dir/vtkmyImagingPythonInitImpl.cxx.s

Imaging/CMakeFiles/vtkmyImagingPythonD.dir/vtkmyImagingPythonInitImpl.cxx.o.requires:
.PHONY : Imaging/CMakeFiles/vtkmyImagingPythonD.dir/vtkmyImagingPythonInitImpl.cxx.o.requires

Imaging/CMakeFiles/vtkmyImagingPythonD.dir/vtkmyImagingPythonInitImpl.cxx.o.provides: Imaging/CMakeFiles/vtkmyImagingPythonD.dir/vtkmyImagingPythonInitImpl.cxx.o.requires
	$(MAKE) -f Imaging/CMakeFiles/vtkmyImagingPythonD.dir/build.make Imaging/CMakeFiles/vtkmyImagingPythonD.dir/vtkmyImagingPythonInitImpl.cxx.o.provides.build
.PHONY : Imaging/CMakeFiles/vtkmyImagingPythonD.dir/vtkmyImagingPythonInitImpl.cxx.o.provides

Imaging/CMakeFiles/vtkmyImagingPythonD.dir/vtkmyImagingPythonInitImpl.cxx.o.provides.build: Imaging/CMakeFiles/vtkmyImagingPythonD.dir/vtkmyImagingPythonInitImpl.cxx.o

# Object files for target vtkmyImagingPythonD
vtkmyImagingPythonD_OBJECTS = \
"CMakeFiles/vtkmyImagingPythonD.dir/vtkImageFooPython.cxx.o" \
"CMakeFiles/vtkmyImagingPythonD.dir/vtkmyImagingPythonInitImpl.cxx.o"

# External object files for target vtkmyImagingPythonD
vtkmyImagingPythonD_EXTERNAL_OBJECTS =

bin/libvtkmyImagingPythonD.dylib: Imaging/CMakeFiles/vtkmyImagingPythonD.dir/vtkImageFooPython.cxx.o
bin/libvtkmyImagingPythonD.dylib: Imaging/CMakeFiles/vtkmyImagingPythonD.dir/vtkmyImagingPythonInitImpl.cxx.o
bin/libvtkmyImagingPythonD.dylib: Imaging/CMakeFiles/vtkmyImagingPythonD.dir/build.make
bin/libvtkmyImagingPythonD.dylib: bin/libvtkmyImaging.dylib
bin/libvtkmyImagingPythonD.dylib: bin/libvtkmyCommonPythonD.dylib
bin/libvtkmyImagingPythonD.dylib: bin/libvtkmyCommon.dylib
bin/libvtkmyImagingPythonD.dylib: Imaging/CMakeFiles/vtkmyImagingPythonD.dir/link.txt
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --red --bold "Linking CXX shared library ../bin/libvtkmyImagingPythonD.dylib"
	cd /Developer/Projects/EclipseWorkspace/vistrails/vistrails/packages/CPCViewer/vtkCPCExtensions/build/Imaging && $(CMAKE_COMMAND) -E cmake_link_script CMakeFiles/vtkmyImagingPythonD.dir/link.txt --verbose=$(VERBOSE)

# Rule to build all files generated by this target.
Imaging/CMakeFiles/vtkmyImagingPythonD.dir/build: bin/libvtkmyImagingPythonD.dylib
.PHONY : Imaging/CMakeFiles/vtkmyImagingPythonD.dir/build

Imaging/CMakeFiles/vtkmyImagingPythonD.dir/requires: Imaging/CMakeFiles/vtkmyImagingPythonD.dir/vtkImageFooPython.cxx.o.requires
Imaging/CMakeFiles/vtkmyImagingPythonD.dir/requires: Imaging/CMakeFiles/vtkmyImagingPythonD.dir/vtkmyImagingPythonInitImpl.cxx.o.requires
.PHONY : Imaging/CMakeFiles/vtkmyImagingPythonD.dir/requires

Imaging/CMakeFiles/vtkmyImagingPythonD.dir/clean:
	cd /Developer/Projects/EclipseWorkspace/vistrails/vistrails/packages/CPCViewer/vtkCPCExtensions/build/Imaging && $(CMAKE_COMMAND) -P CMakeFiles/vtkmyImagingPythonD.dir/cmake_clean.cmake
.PHONY : Imaging/CMakeFiles/vtkmyImagingPythonD.dir/clean

Imaging/CMakeFiles/vtkmyImagingPythonD.dir/depend: Imaging/vtkImageFooPython.cxx
Imaging/CMakeFiles/vtkmyImagingPythonD.dir/depend: Imaging/vtkmyImagingPythonInit.cxx
Imaging/CMakeFiles/vtkmyImagingPythonD.dir/depend: Imaging/vtkmyImagingPythonInitImpl.cxx
	cd /Developer/Projects/EclipseWorkspace/vistrails/vistrails/packages/CPCViewer/vtkCPCExtensions/build && $(CMAKE_COMMAND) -E cmake_depends "Unix Makefiles" /Developer/Projects/EclipseWorkspace/vistrails/vistrails/packages/CPCViewer/vtkCPCExtensions/vtkMy /Developer/Projects/EclipseWorkspace/vistrails/vistrails/packages/CPCViewer/vtkCPCExtensions/vtkMy/Imaging /Developer/Projects/EclipseWorkspace/vistrails/vistrails/packages/CPCViewer/vtkCPCExtensions/build /Developer/Projects/EclipseWorkspace/vistrails/vistrails/packages/CPCViewer/vtkCPCExtensions/build/Imaging /Developer/Projects/EclipseWorkspace/vistrails/vistrails/packages/CPCViewer/vtkCPCExtensions/build/Imaging/CMakeFiles/vtkmyImagingPythonD.dir/DependInfo.cmake --color=$(COLOR)
.PHONY : Imaging/CMakeFiles/vtkmyImagingPythonD.dir/depend

