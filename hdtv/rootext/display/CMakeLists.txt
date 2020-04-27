cmake_minimum_required(VERSION 3.6 FATAL_ERROR)

project(display LANGUAGES CXX)

set(SOURCES
    Calibration.cc
    DisplayBlock.cc
    DisplayCut.cc
    DisplayFunc.cc
    DisplayObj.cc
    DisplaySpec.cc
    DisplayStack.cc
    Marker.cc
    MTViewer.cc
    Painter.cc
    View1D.cc
    View2D.cc
    View.cc
    Viewer.cc
    XMarker.cc
    YMarker.cc)

set(HEADERS
    Calibration.hh
    DisplayBlock.hh
    DisplayCut.hh
    DisplayFunc.hh
    DisplayObj.hh
    DisplayObjZIndex.hh
    DisplaySpec.hh
    DisplayStack.hh
    Marker.hh
    MTViewer.hh
    Painter.hh
    View1D.hh
    View2D.hh
    Viewer.hh
    View.hh
    XMarker.hh
    YMarker.hh)

find_package(X11 REQUIRED)

find_package(ROOT REQUIRED COMPONENTS Core Hist Graf)
message(STATUS "ROOT Version ${ROOT_VERSION} found in ${ROOT_root_CMD}")
include(${ROOT_DIR}/RootMacros.cmake)

root_generate_dictionary(G__${PROJECT_NAME} ${HEADERS} LINKDEF LinkDef.h)

add_library(${PROJECT_NAME} SHARED ${SOURCES} G__${PROJECT_NAME}.cxx)
add_library(hdtv::${PROJECT_NAME} ALIAS ${PROJECT_NAME})

target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_14)
set_target_properties(
  ${PROJECT_NAME}
  PROPERTIES
    RESOURCE
    "${CMAKE_CURRENT_BINARY_DIR}/lib${PROJECT_NAME}.rootmap;${CMAKE_CURRENT_BINARY_DIR}/lib${PROJECT_NAME}_rdict.pcm"
)
target_include_directories(${PROJECT_NAME} PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
target_link_libraries(${PROJECT_NAME} ROOT::Core ROOT::Hist ROOT::Graf X11)

# Install
include(GNUInstallDirs)
install(
  TARGETS ${PROJECT_NAME}
  LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
  ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
  RESOURCE DESTINATION ${CMAKE_INSTALL_LIBDIR})
