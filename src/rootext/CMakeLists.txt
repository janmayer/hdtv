cmake_minimum_required(VERSION 3.15)

project(${SKBUILD_PROJECT_NAME} LANGUAGES C CXX)

find_package(ROOT 6.20 CONFIG REQUIRED)
include(${ROOT_DIR}/RootMacros.cmake)
set(CMAKE_CXX_FLAGS ${ROOT_CXX_FLAGS})

if(UNIX AND NOT APPLE)
  find_package(X11 REQUIRED)
endif()


add_subdirectory(calibration)
add_subdirectory(display)
add_subdirectory(fit)
add_subdirectory(mfile-root)
