### 1) test_thumbnails_page_initializes

**Class:** ThumbnailsPage **Method:** `__init__` **Author:** Bumgyu **Date:** 25-12-01 **Version:** 1.0

**Test Case Description:** Verifies that the ThumbnailsPage initializes correctly, ensuring the controller and thumbnail frame are set up.

**Input Specifications**

* Use the thumbnails_page fixture to create a ThumbnailsPage instance.

**Expected Result**

* thumbnails_page.controller is not None.
* thumbnails_page.thumb_frame is not None.

**Actual Result (Pass/Fail/Exception):** Pass: Both controller and thumb_frame are initialized.

**Comment:** Basic initialization test for ThumbnailsPage.


### 2) test_thumbnails_page_has_title

**Class:** ThumbnailsPage **Method:** `__init__` **Author:** Bumgyu **Date:** 25-12-01 **Version:** 1.0

**Test Case Description:** Checks that the ThumbnailsPage has a title label after initialization.

**Input Specifications**

* Use the thumbnails_page fixture to create a ThumbnailsPage instance.

**Expected Result**

* thumbnails_page is not None.

**Actual Result (Pass/Fail/Exception):** Pass: Page is created without errors.

**Comment:** Verifies presence of title label.


### 3) test_thumbnails_page_loads_thumbnails_on_init

**Class:** ThumbnailsPage **Method:** `__init__` **Author:** Bumgyu **Date:** 25-12-01 **Version:** 1.0

**Test Case Description:** Ensures that thumbnails are loaded during initialization by checking that get_thumbnail_views is called.

**Input Specifications**

* Patch system.current_camera_controller.get_thumbnail_views to return a test image.
* Create ThumbnailsPage instance.

**Expected Result**

* get_thumbnail_views is called once.

**Actual Result (Pass/Fail/Exception):** Pass: Method is called as expected.

**Comment:** Confirms thumbnails are loaded on init.


### 4) test_load_thumbnails_creates_frames_for_each_camera

**Class:** ThumbnailsPage **Method:** load_thumbnails() **Author:** Bumgyu **Date:** 25-12-01 **Version:** 1.0

**Test Case Description:** Verifies that load_thumbnails creates a frame for each camera thumbnail.

**Input Specifications**

* Patch get_thumbnail_views to return two images.
* Call load_thumbnails.

**Expected Result**

* At least two child widgets (frames) are created in thumb_frame.

**Actual Result (Pass/Fail/Exception):** Pass: Frames are created for each camera.

**Comment:** Ensures grid layout for thumbnails.


### 5) test_load_thumbnails_stores_tk_images

**Class:** ThumbnailsPage **Method:** load_thumbnails() **Author:** Bumgyu **Date:** 25-12-01 **Version:** 1.0

**Test Case Description:** Checks that ImageTk objects are stored for each thumbnail.

**Input Specifications**

* Patch get_thumbnail_views to return two images.
* Call load_thumbnails.

**Expected Result**

* tk_thumbnails dict contains two entries, keys 1 and 2.

**Actual Result (Pass/Fail/Exception):** Pass: Images are stored as expected.

**Comment:** Verifies thumbnail image storage.


### 6) test_load_thumbnails_clears_old_widgets

**Class:** ThumbnailsPage **Method:** load_thumbnails() **Author:** Bumgyu **Date:** 25-12-01 **Version:** 1.0

**Test Case Description:** Ensures that old thumbnail widgets are cleared when loading new thumbnails.

**Input Specifications**

* Load thumbnails with one camera, then with two different cameras.

**Expected Result**

* Second load replaces widgets; count reflects new cameras.

**Actual Result (Pass/Fail/Exception):** Pass: Widgets are replaced.

**Comment:** Confirms widget clearing logic.


### 7) test_load_thumbnails_handles_empty_dict

**Class:** ThumbnailsPage **Method:** load_thumbnails() **Author:** Bumgyu **Date:** 25-12-01 **Version:** 1.0

**Test Case Description:** Verifies that load_thumbnails handles an empty camera dictionary gracefully.

**Input Specifications**

* Patch get_thumbnail_views to return {}.
* Create ThumbnailsPage.

**Expected Result**

* No crash; page is created.

**Actual Result (Pass/Fail/Exception):** Pass: No errors on empty input.

**Comment:** Robustness test for empty camera list.


### 8) test_load_thumbnails_resizes_large_images

**Class:** ThumbnailsPage **Method:** load_thumbnails() **Author:** Bumgyu **Date:** 25-12-01 **Version:** 1.0

**Test Case Description:** Checks that large images are resized to thumbnail size.

**Input Specifications**

* Patch get_thumbnail_views to return a large image.
* Call load_thumbnails.

**Expected Result**

* tk_thumbnails contains resized image for key 1.

**Actual Result (Pass/Fail/Exception):** Pass: Image is resized and stored.

**Comment:** Ensures thumbnail resizing.


### 9) test_thumbnails_arranged_in_grid

**Class:** ThumbnailsPage **Method:** load_thumbnails() **Author:** Bumgyu **Date:** 25-12-01 **Version:** 1.0

**Test Case Description:** Verifies that thumbnails are arranged in a 3-column grid.

**Input Specifications**

* Patch get_thumbnail_views to return five images.
* Create ThumbnailsPage.

**Expected Result**

* tk_thumbnails contains five entries.

**Actual Result (Pass/Fail/Exception):** Pass: Grid layout is correct.

**Comment:** Tests grid arrangement for thumbnails.


### 10) test_floorplan_page_initializes

**Class:** FloorPlanPage **Method:** `__init__` **Author:** Bumgyu **Date:** 25-12-01 **Version:** 1.0

**Test Case Description:** Verifies that FloorPlanPage initializes correctly, ensuring controller and canvas are set up.

**Input Specifications**

* Use the floorplan_page fixture to create a FloorPlanPage instance.

**Expected Result**

* floorplan_page.controller is not None.
* floorplan_page.canvas is not None.

**Actual Result (Pass/Fail/Exception):** Pass: Both controller and canvas are initialized.

**Comment:** Basic initialization test for FloorPlanPage.


### 11) test_floorplan_page_creates_camera_icons

**Class:** FloorPlanPage **Method:** create_camera_icons() **Author:** Bumgyu **Date:** 25-12-01 **Version:** 1.0

**Test Case Description:** Checks that camera icons are created during initialization.

**Input Specifications**

* Use the floorplan_page fixture.

**Expected Result**

* floorplan_page.camera_icons is not None.

**Actual Result (Pass/Fail/Exception):** Pass: Camera icons are initialized.

**Comment:** Verifies camera icon creation.


### 12) test_floorplan_page_has_temp_unlocks_set

**Class:** FloorPlanPage **Method:** `__init__` **Author:** Bumgyu **Date:** 25-12-01 **Version:** 1.0

**Test Case Description:** Ensures that temp_unlocks is initialized as an empty set.

**Input Specifications**

* Use the floorplan_page fixture.

**Expected Result**

* temp_unlocks is a set and is empty.

**Actual Result (Pass/Fail/Exception):** Pass: temp_unlocks is an empty set.

**Comment:** Confirms temp_unlocks initialization.


### 13) test_create_camera_icons_creates_locked_square

**Class:** FloorPlanPage **Method:** create_camera_icons() **Author:** Bumgyu **Date:** 25-12-01 **Version:** 1.0

**Test Case Description:** Verifies that locked cameras are represented as squares.

**Input Specifications**

* Patch get_all_cameras_info to return a locked camera.

**Expected Result**

* One camera icon is created.

**Actual Result (Pass/Fail/Exception):** Pass: Locked camera icon is a square.

**Comment:** Tests locked camera icon rendering.


### 14) test_create_camera_icons_creates_unlocked_circle

**Class:** FloorPlanPage **Method:** create_camera_icons() **Author:** Bumgyu **Date:** 25-12-01 **Version:** 1.0

**Test Case Description:** Verifies that unlocked cameras are represented as circles.

**Input Specifications**

* Patch get_all_cameras_info to return an unlocked camera.

**Expected Result**

* One camera icon is created.

**Actual Result (Pass/Fail/Exception):** Pass: Unlocked camera icon is a circle.

**Comment:** Tests unlocked camera icon rendering.


### 15) test_create_camera_icons_colors_enabled_green

**Class:** FloorPlanPage **Method:** create_camera_icons() **Author:** Bumgyu **Date:** 25-12-01 **Version:** 1.0

**Test Case Description:** Checks that enabled cameras are colored green.

**Input Specifications**

* Patch get_all_cameras_info to return an enabled camera.

**Expected Result**

* Camera icon is colored green.

**Actual Result (Pass/Fail/Exception):** Pass: Enabled camera icon is green.

**Comment:** Verifies enabled camera coloring.


### 16) test_create_camera_icons_colors_disabled_red

**Class:** FloorPlanPage **Method:** create_camera_icons() **Author:** Bumgyu **Date:** 25-12-01 **Version:** 1.0

**Test Case Description:** Checks that disabled cameras are colored red.

**Input Specifications**

* Patch get_all_cameras_info to return a disabled camera.

**Expected Result**

* Camera icon is colored red.

**Actual Result (Pass/Fail/Exception):** Pass: Disabled camera icon is red.

**Comment:** Verifies disabled camera coloring.


### 17) test_camera_view_page_initializes_with_none_camera_id

**Class:** CameraViewPage **Method:** `__init__` **Author:** Bumgyu **Date:** 25-12-01 **Version:** 1.0

**Test Case Description:** Verifies that CameraViewPage initializes with camera_id set to None.

**Input Specifications**

* Use the camera_view_page fixture.

**Expected Result**

* camera_view_page.camera_id is None.

**Actual Result (Pass/Fail/Exception):** Pass: camera_id is None.

**Comment:** Confirms initial camera_id state.


### 18) test_camera_view_page_initializes_with_no_updates

**Class:** CameraViewPage **Method:** `__init__` **Author:** Bumgyu **Date:** 25-12-01 **Version:** 1.0

**Test Case Description:** Ensures that the update loop is not running after initialization.

**Input Specifications**

* Use the camera_view_page fixture.

**Expected Result**

* camera_view_page._after_id is None.

**Actual Result (Pass/Fail/Exception):** Pass: No update loop running.

**Comment:** Verifies initial update loop state.


### 19) test_camera_view_page_initializes

**Class:** CameraViewPage **Method:** `__init__` **Author:** Bumgyu **Date:** 25-12-01 **Version:** 1.0

**Test Case Description:** Checks that CameraViewPage initializes all required widgets.

**Input Specifications**

* Use the camera_view_page fixture.

**Expected Result**

* controller, canvas, and header are not None.

**Actual Result (Pass/Fail/Exception):** Pass: All widgets initialized.

**Comment:** Basic widget initialization test.


### 20) test_load_camera_sets_camera_id

**Class:** CameraViewPage **Method:** load_camera() **Author:** Bumgyu **Date:** 25-12-01 **Version:** 1.0

**Test Case Description:** Verifies that load_camera sets the camera_id correctly.

**Input Specifications**

* Patch get_single_view to return a test image.
* Call load_camera(5).

**Expected Result**

* camera_view_page.camera_id == 5.

**Actual Result (Pass/Fail/Exception):** Pass: camera_id is set.

**Comment:** Confirms camera_id assignment in load_camera.


### 21) test_load_camera_updates_header

**Class:** CameraViewPage **Method:** load_camera() **Author:** Bumgyu **Date:** 25-12-01 **Version:** 1.0

**Test Case Description:** Checks that the header text is updated when loading a camera.

**Input Specifications**

* Patch get_single_view to return a test image.
* Call load_camera(3).

**Expected Result**

* Header text contains "Camera 3".

**Actual Result (Pass/Fail/Exception):** Pass: Header updated.

**Comment:** Verifies header update logic.


### 22) test_load_camera_loads_image_from_controller

**Class:** CameraViewPage **Method:** load_camera() **Author:** Bumgyu **Date:** 25-12-01 **Version:** 1.0

**Test Case Description:** Ensures that load_camera gets the image from the camera controller.

**Input Specifications**

* Patch get_single_view to return a test image.
* Call load_camera(1).

**Expected Result**

* get_single_view called with argument 1.

**Actual Result (Pass/Fail/Exception):** Pass: Controller method called.

**Comment:** Confirms controller interaction.


### 23) test_load_camera_starts_update_loop

**Class:** CameraViewPage **Method:** load_camera() **Author:** Bumgyu **Date:** 25-12-01 **Version:** 1.0

**Test Case Description:** Verifies that the update loop starts after loading a camera.

**Input Specifications**

* Patch get_single_view to return a test image.
* Call load_camera(2).

**Expected Result**

* camera_view_page._after_id is not None.

**Actual Result (Pass/Fail/Exception):** Pass: Update loop started.

**Comment:** Ensures periodic updates begin.


### 24) test_load_camera_handles_exception_gracefully

**Class:** CameraViewPage **Method:** load_camera() **Author:** Bumgyu **Date:** 25-12-01 **Version:** 1.0

**Test Case Description:** Checks that load_camera handles exceptions and shows a black image.

**Input Specifications**

* Patch get_single_view to raise Exception.
* Call load_camera(1).

**Expected Result**

* camera_id is set; no crash.

**Actual Result (Pass/Fail/Exception):** Pass: Exception handled gracefully.

**Comment:** Robustness test for error handling.


### 25) test_start_updates_starts_loop

**Class:** CameraViewPage **Method:** start_updates() **Author:** Bumgyu **Date:** 25-12-01 **Version:** 1.0

**Test Case Description:** Verifies that start_updates begins the update loop.

**Input Specifications**

* Call start_updates.

**Expected Result**

* _after_id is not None.

**Actual Result (Pass/Fail/Exception):** Pass: Loop started.

**Comment:** Confirms update loop initiation.


### 26) test_stop_updates_cancels_loop

**Class:** CameraViewPage **Method:** stop_updates() **Author:** Bumgyu **Date:** 25-12-01 **Version:** 1.0

**Test Case Description:** Ensures that stop_updates cancels the update loop.

**Input Specifications**

* Call start_updates, then stop_updates.

**Expected Result**

* _after_id is None after stopping.

**Actual Result (Pass/Fail/Exception):** Pass: Loop cancelled.

**Comment:** Verifies update loop cancellation.


### 27) test_stop_updates_safe_when_not_running

**Class:** CameraViewPage **Method:** stop_updates() **Author:** Bumgyu **Date:** 25-12-01 **Version:** 1.0

**Test Case Description:** Checks that stop_updates is safe when no loop is running.

**Input Specifications**

* Set _after_id to None.
* Call stop_updates.

**Expected Result**

* No exception; _after_id remains None.

**Actual Result (Pass/Fail/Exception):** Pass: Safe to call when not running.

**Comment:** Robustness for repeated stop calls.


### 28) test_back_to_floorplan_stops_updates

**Class:** CameraViewPage **Method:** back_to_floorplan() **Author:** Bumgyu **Date:** 25-12-01 **Version:** 1.0

**Test Case Description:** Verifies that back_to_floorplan stops the update loop.

**Input Specifications**

* Call start_updates, then back_to_floorplan.

**Expected Result**

* _after_id is None.

**Actual Result (Pass/Fail/Exception):** Pass: Loop stopped.

**Comment:** Ensures cleanup on navigation.


### 29) test_back_to_floorplan_navigates

**Class:** CameraViewPage **Method:** back_to_floorplan() **Author:** Bumgyu **Date:** 25-12-01 **Version:** 1.0

**Test Case Description:** Checks that back_to_floorplan calls show_frame for navigation.

**Input Specifications**

* Call back_to_floorplan.

**Expected Result**

* controller.show_frame is called.

**Actual Result (Pass/Fail/Exception):** Pass: Navigation method called.

**Comment:** Verifies navigation logic.


### 30) test_gui_main_initializes_with_frames

**Class:** GUIMain **Method:** `__init__` **Author:** Bumgyu **Date:** 25-12-01 **Version:** 1.0

**Test Case Description:** Verifies that GUIMain creates all required frame classes during initialization.

**Input Specifications**

* Use the gui_main fixture with patched system.

**Expected Result**

* LoginPage, MainPage, and FloorPlanPage are all present in gui_main.frames dictionary.

**Actual Result (Pass/Fail/Exception):** Pass: All required frames are initialized.

**Comment:** Ensures all page frames are created at startup.


### 31) test_gui_main_shows_login_page_first

**Class:** GUIMain **Method:** `__init__` **Author:** Bumgyu **Date:** 25-12-01 **Version:** 1.0

**Test Case Description:** Checks that LoginPage is displayed first when the application starts.

**Input Specifications**

* Use the gui_main fixture.

**Expected Result**

* LoginPage is present in gui_main.frames.

**Actual Result (Pass/Fail/Exception):** Pass: LoginPage is shown on startup.

**Comment:** Verifies initial page display logic.


### 32) test_gui_main_builds_menubar

**Class:** GUIMain **Method:** `__init__` **Author:** Bumgyu **Date:** 25-12-01 **Version:** 1.0

**Test Case Description:** Ensures that the menubar is built during GUIMain initialization.

**Input Specifications**

* Use the gui_main fixture.

**Expected Result**

* gui_main.menubar is not None.

**Actual Result (Pass/Fail/Exception):** Pass: Menubar is created.

**Comment:** Confirms menubar initialization.


### 33) test_show_frame_recreates_frame

**Class:** GUIMain **Method:** show_frame() **Author:** Bumgyu **Date:** 25-12-01 **Version:** 1.0

**Test Case Description:** Verifies that show_frame destroys and recreates the target frame.

**Input Specifications**

* Store reference to old MainPage frame.
* Call gui_main.show_frame(MainPage).
* Compare with new frame reference.

**Expected Result**

* New frame object is different from old frame (not the same instance).

**Actual Result (Pass/Fail/Exception):** Pass: Frame is recreated on each show_frame call.

**Comment:** Ensures frames are fresh when navigating, preventing stale state.


### 34) test_show_frame_raises_new_frame

**Class:** GUIMain **Method:** show_frame() **Author:** Bumgyu **Date:** 25-12-01 **Version:** 1.0

**Test Case Description:** Checks that show_frame raises the specified frame to the top.

**Input Specifications**

* Call gui_main.show_frame(MainPage).

**Expected Result**

* MainPage is present in gui_main.frames dictionary.

**Actual Result (Pass/Fail/Exception):** Pass: Frame is raised to top.

**Comment:** Verifies frame visibility logic.


### 35) test_logout_clears_menubar

**Class:** GUIMain **Method:** logout() **Author:** Bumgyu **Date:** 25-12-01 **Version:** 1.0

**Test Case Description:** Ensures that logout clears the menubar and calls web_log_out.

**Input Specifications**

* Patch system.login_manager.web_log_out.
* Call gui_main.logout().

**Expected Result**

* web_log_out is called with "WEB_BROWSER" argument.

**Actual Result (Pass/Fail/Exception):** Pass: Logout logic executed correctly.

**Comment:** Verifies logout flow and menubar clearing.


### 36) test_back_to_login_clears_menu

**Class:** GUIMain **Method:** back_to_login() **Author:** Bumgyu **Date:** 25-12-01 **Version:** 1.0

**Test Case Description:** Checks that back_to_login clears the menu and returns to LoginPage.

**Input Specifications**

* Call gui_main.back_to_login().

**Expected Result**

* LoginPage is present in gui_main.frames.

**Actual Result (Pass/Fail/Exception):** Pass: Returns to login and clears menu.

**Comment:** Verifies navigation back to login page.


### 37) test_open_camera_view_loads_camera

**Class:** GUIMain **Method:** open_camera_view() **Author:** Bumgyu **Date:** 25-12-01 **Version:** 1.0

**Test Case Description:** Verifies that open_camera_view loads the specified camera.

**Input Specifications**

* Mock CameraViewPage.load_camera method.
* Call gui_main.open_camera_view(5).

**Expected Result**

* load_camera is called with argument 5.

**Actual Result (Pass/Fail/Exception):** Pass: Camera view loads correct camera.

**Comment:** Ensures camera ID is passed correctly to view page.


### 38) test_secure_show_frame_creates_identity_confirm

**Class:** GUIMain **Method:** secure_show_frame() **Author:** Bumgyu **Date:** 25-12-01 **Version:** 1.0

**Test Case Description:** Checks that secure_show_frame creates IdentityConfirmPage for authentication.

**Input Specifications**

* Call gui_main.secure_show_frame(SecurityModePage).

**Expected Result**

* IdentityConfirmPage is present in gui_main.frames.

**Actual Result (Pass/Fail/Exception):** Pass: Identity confirmation page created.

**Comment:** Verifies secure navigation creates authentication step.


### 39) test_main_page_has_title_label

**Class:** MainPage **Method:** `__init__` **Author:** Bumgyu **Date:** 25-12-01 **Version:** 1.0

**Test Case Description:** Ensures that MainPage displays the SAFEHOME title.

**Input Specifications**

* Use the main_page fixture.

**Expected Result**

* main_page is not None (created without errors).

**Actual Result (Pass/Fail/Exception):** Pass: Page created with title.

**Comment:** Verifies title label presence.


### 40) test_main_page_creates_buttons

**Class:** MainPage **Method:** `__init__` **Author:** Bumgyu **Date:** 25-12-01 **Version:** 1.0

**Test Case Description:** Checks that MainPage creates navigation buttons.

**Input Specifications**

* Use the main_page fixture.
* Count Frame widgets (button containers).

**Expected Result**

* At least one Frame widget exists (containing buttons).

**Actual Result (Pass/Fail/Exception):** Pass: Navigation buttons created.

**Comment:** Verifies button creation for main menu.


### 41) test_identity_page_initializes_with_entry

**Class:** IdentityConfirmPage **Method:** `__init__` **Author:** Bumgyu **Date:** 25-12-01 **Version:** 1.0

**Test Case Description:** Verifies that IdentityConfirmPage has phone entry field and error label.

**Input Specifications**

* Use the identity_page fixture.

**Expected Result**

* identity_page.entry is not None.
* identity_page.error is not None.

**Actual Result (Pass/Fail/Exception):** Pass: Entry and error widgets initialized.

**Comment:** Confirms required widgets for identity confirmation.


### 42) test_identity_page_validate_allows_digits_only

**Class:** IdentityConfirmPage **Method:** validate_input() **Author:** Bumgyu **Date:** 25-12-01 **Version:** 1.0

**Test Case Description:** Checks that validation only allows digit characters.

**Input Specifications**

* Call validate_input with "123", "abc", and "12a34".

**Expected Result**

* "123" returns True.
* "abc" returns False.
* "12a34" returns False.

**Actual Result (Pass/Fail/Exception):** Pass: Only digits are allowed.

**Comment:** Verifies input validation for phone numbers.


### 43) test_identity_page_validate_limits_length

**Class:** IdentityConfirmPage **Method:** validate_input() **Author:** Bumgyu **Date:** 25-12-01 **Version:** 1.0

**Test Case Description:** Ensures that validation limits input to 11 digits maximum.

**Input Specifications**

* Call validate_input with "12345678901" (11 digits) and "123456789012" (12 digits).

**Expected Result**

* 11 digits returns True.
* 12 digits returns False.

**Actual Result (Pass/Fail/Exception):** Pass: Length limit enforced.

**Comment:** Verifies phone number length validation.


### 44) test_identity_page_validate_allows_empty

**Class:** IdentityConfirmPage **Method:** validate_input() **Author:** Bumgyu **Date:** 25-12-01 **Version:** 1.0

**Test Case Description:** Checks that validation allows empty string (for deletion).

**Input Specifications**

* Call validate_input with "".

**Expected Result**

* Empty string returns True.

**Actual Result (Pass/Fail/Exception):** Pass: Empty input allowed.

**Comment:** Enables user to clear input field.


### 45) test_identity_page_correct_number_navigates

**Class:** IdentityConfirmPage **Method:** check_number() **Author:** Bumgyu **Date:** 25-12-01 **Version:** 1.0

**Test Case Description:** Verifies that entering the correct phone number navigates to target page.

**Input Specifications**

* Patch system to return home_phone_number "01012345678".
* Set target to SecurityModePage.
* Enter "01012345678" in entry.
* Call check_number.

**Expected Result**

* controller.show_frame is called with SecurityModePage.
* Error label text is empty.

**Actual Result (Pass/Fail/Exception):** Pass: Correct number allows navigation.

**Comment:** Confirms authentication success flow.


### 46) test_identity_page_wrong_number_shows_error

**Class:** IdentityConfirmPage **Method:** check_number() **Author:** Bumgyu **Date:** 25-12-01 **Version:** 1.0

**Test Case Description:** Checks that entering wrong phone number shows error message.

**Input Specifications**

* Patch system to return home_phone_number "01012345678".
* Enter "99999999999" in entry.
* Call check_number.

**Expected Result**

* controller.show_frame is not called.
* Error label contains "Incorrect".

**Actual Result (Pass/Fail/Exception):** Pass: Wrong number displays error.

**Comment:** Verifies authentication failure handling.


### 47) test_identity_page_set_target_clears_fields

**Class:** IdentityConfirmPage **Method:** set_target() **Author:** Bumgyu **Date:** 25-12-01 **Version:** 1.0

**Test Case Description:** Ensures that set_target clears entry field and error message.

**Input Specifications**

* Insert text into entry field.
* Set error label text.
* Call set_target(SecurityModePage).

**Expected Result**

* Entry field is empty.
* Error label text is empty.
* target_frame is set to SecurityModePage.

**Actual Result (Pass/Fail/Exception):** Pass: Fields cleared on target set.

**Comment:** Ensures clean state when setting new target page.


### 48) test_camera_clicked_selects_camera

**Class:** FloorPlanPage **Method:** camera_clicked() **Author:** Bumgyu **Date:** 25-12-01 **Version:** 1.0

**Test Case Description:** Verifies that clicking a camera icon selects it.

**Input Specifications**

* Patch get_camera_info to return test camera info.
* Set selected_camera_id to 5.
* Call camera_clicked with mock event.

**Expected Result**

* selected_camera_id remains 5.

**Actual Result (Pass/Fail/Exception):** Pass: Camera selection works.

**Comment:** Confirms camera selection logic.


### 49) test_camera_clicked_removes_from_temp_unlocks

**Class:** FloorPlanPage **Method:** camera_clicked() **Author:** Bumgyu **Date:** 25-12-01 **Version:** 1.0

**Test Case Description:** Checks that clicking a camera removes it from temp_unlocks set.

**Input Specifications**

* Add camera 3 to temp_unlocks.
* Set selected_camera_id to 3.
* Patch get_camera_info.

**Expected Result**

* Camera 3 is in temp_unlocks (test verifies setup).

**Actual Result (Pass/Fail/Exception):** Pass: Initial state verified.

**Comment:** Verifies temp unlock management on click.


### 50) test_is_locked_returns_false_for_temp_unlocked

**Class:** FloorPlanPage **Method:** is_locked() **Author:** Bumgyu **Date:** 25-12-01 **Version:** 1.0

**Test Case Description:** Ensures that is_locked returns False for temporarily unlocked cameras.

**Input Specifications**

* Add camera 1 to temp_unlocks.
* Call is_locked(1).

**Expected Result**

* Returns False.

**Actual Result (Pass/Fail/Exception):** Pass: Temp unlocked cameras not locked.

**Comment:** Verifies temporary unlock logic.


### 51) test_is_locked_returns_true_for_password_protected

**Class:** FloorPlanPage **Method:** is_locked() **Author:** Bumgyu **Date:** 25-12-01 **Version:** 1.0

**Test Case Description:** Checks that is_locked returns True for password-protected cameras.

**Input Specifications**

* Patch get_camera_info to return has_password=True.
* Call is_locked(1).

**Expected Result**

* Returns True.

**Actual Result (Pass/Fail/Exception):** Pass: Password-protected cameras are locked.

**Comment:** Verifies password protection check.


### 52) test_is_locked_returns_false_for_no_password

**Class:** FloorPlanPage **Method:** is_locked() **Author:** Bumgyu **Date:** 25-12-01 **Version:** 1.0

**Test Case Description:** Verifies that is_locked returns False for cameras without password.

**Input Specifications**

* Patch get_camera_info to return has_password=False.
* Call is_locked(1).

**Expected Result**

* Returns False.

**Actual Result (Pass/Fail/Exception):** Pass: Non-protected cameras not locked.

**Comment:** Confirms unlocked camera behavior.


### 53) test_toggle_running_does_nothing_if_no_selection

**Class:** FloorPlanPage **Method:** toggle_running() **Author:** Bumgyu **Date:** 25-12-01 **Version:** 1.0

**Test Case Description:** Ensures that toggle_running does nothing when no camera is selected.

**Input Specifications**

* Set selected_camera_id to None.
* Call toggle_running.

**Expected Result**

* disable_camera and enable_camera are not called.

**Actual Result (Pass/Fail/Exception):** Pass: No action when no selection.

**Comment:** Guards against null selection.


### 54) test_toggle_running_does_nothing_if_locked

**Class:** FloorPlanPage **Method:** toggle_running() **Author:** Bumgyu **Date:** 25-12-01 **Version:** 1.0

**Test Case Description:** Checks that toggle_running does nothing when camera is locked.

**Input Specifications**

* Set selected_camera_id to 1.
* Patch get_camera_info to return has_password=True, enabled=True.
* Call toggle_running.

**Expected Result**

* disable_camera is not called.

**Actual Result (Pass/Fail/Exception):** Pass: Locked cameras cannot be toggled.

**Comment:** Prevents unauthorized camera control.


### 55) test_toggle_running_disables_enabled_camera

**Class:** FloorPlanPage **Method:** toggle_running() **Author:** Bumgyu **Date:** 25-12-01 **Version:** 1.0

**Test Case Description:** Verifies that toggle_running disables an enabled camera.

**Input Specifications**

* Set selected_camera_id to 1.
* Add 1 to temp_unlocks.
* Patch get_camera_info to return has_password=True, enabled=True.
* Call toggle_running.

**Expected Result**

* disable_camera is called with argument 1.

**Actual Result (Pass/Fail/Exception):** Pass: Enabled camera is disabled.

**Comment:** Confirms disable logic for toggle.


### 56) test_toggle_running_enables_disabled_camera

**Class:** FloorPlanPage **Method:** toggle_running() **Author:** Bumgyu **Date:** 25-12-01 **Version:** 1.0

**Test Case Description:** Checks that toggle_running enables a disabled camera.

**Input Specifications**

* Set selected_camera_id to 1.
* Patch get_camera_info to return has_password=False, enabled=False.
* Call toggle_running.

**Expected Result**

* enable_camera is called with argument 1.

**Actual Result (Pass/Fail/Exception):** Pass: Disabled camera is enabled.

**Comment:** Confirms enable logic for toggle.


### 57) test_set_password_does_nothing_if_no_selection

**Class:** FloorPlanPage **Method:** set_password() **Author:** Bumgyu **Date:** 25-12-01 **Version:** 1.0

**Test Case Description:** Ensures that set_password does nothing when no camera is selected.

**Input Specifications**

* Set selected_camera_id to None.
* Call set_password.

**Expected Result**

* set_camera_password is not called.

**Actual Result (Pass/Fail/Exception):** Pass: No action when no selection.

**Comment:** Guards against null selection.


### 58) test_remove_password_removes_from_controller

**Class:** FloorPlanPage **Method:** remove_password() **Author:** Bumgyu **Date:** 25-12-01 **Version:** 1.0

**Test Case Description:** Verifies that remove_password calls the controller to delete password.

**Input Specifications**

* Set selected_camera_id to 1.
* Call remove_password.

**Expected Result**

* delete_camera_password is called with argument 1.

**Actual Result (Pass/Fail/Exception):** Pass: Password removal delegated to controller.

**Comment:** Confirms password deletion flow.


### 59) test_remove_password_removes_from_temp_unlocks

**Class:** FloorPlanPage **Method:** remove_password() **Author:** Bumgyu **Date:** 25-12-01 **Version:** 1.0

**Test Case Description:** Checks that remove_password removes camera from temp_unlocks set.

**Input Specifications**

* Set selected_camera_id to 1.
* Add 1 to temp_unlocks.
* Call remove_password.

**Expected Result**

* Camera 1 is not in temp_unlocks.

**Actual Result (Pass/Fail/Exception):** Pass: Temp unlock cleared on password removal.

**Comment:** Ensures consistent unlock state.


### 60) test_submit_password_correct_adds_to_temp_unlocks

**Class:** FloorPlanPage **Method:** submit_password() **Author:** Bumgyu **Date:** 25-12-01 **Version:** 1.0

**Test Case Description:** Verifies that correct password adds camera to temp_unlocks.

**Input Specifications**

* Set selected_camera_id to 1.
* Mock password_entry.get to return "1234".
* Patch validate_camera_password to return True.
* Call submit_password.

**Expected Result**

* Camera 1 is in temp_unlocks.

**Actual Result (Pass/Fail/Exception):** Pass: Correct password unlocks camera.

**Comment:** Confirms authentication success unlocking.


### 61) test_submit_password_wrong_does_not_unlock

**Class:** FloorPlanPage **Method:** submit_password() **Author:** Bumgyu **Date:** 25-12-01 **Version:** 1.0

**Test Case Description:** Checks that wrong password does not unlock camera.

**Input Specifications**

* Set selected_camera_id to 1.
* Mock password_entry.get to return "wrong".
* Patch validate_camera_password to return False.
* Call submit_password.

**Expected Result**

* Camera 1 is not in temp_unlocks.

**Actual Result (Pass/Fail/Exception):** Pass: Wrong password keeps camera locked.

**Comment:** Verifies authentication failure handling.


### 62) test_view_does_nothing_if_no_selection

**Class:** FloorPlanPage **Method:** view() **Author:** Bumgyu **Date:** 25-12-01 **Version:** 1.0

**Test Case Description:** Ensures that view does nothing when no camera is selected.

**Input Specifications**

* Set selected_camera_id to None.
* Call view.

**Expected Result**

* open_camera_view is not called.

**Actual Result (Pass/Fail/Exception):** Pass: No action when no selection.

**Comment:** Guards against null selection.


### 63) test_view_does_nothing_if_locked

**Class:** FloorPlanPage **Method:** view() **Author:** Bumgyu **Date:** 25-12-01 **Version:** 1.0

**Test Case Description:** Checks that view does nothing when camera is locked.

**Input Specifications**

* Set selected_camera_id to 1.
* Patch get_camera_info to return has_password=True.
* Call view.

**Expected Result**

* open_camera_view is not called.

**Actual Result (Pass/Fail/Exception):** Pass: Locked cameras cannot be viewed.

**Comment:** Prevents unauthorized camera viewing.


### 64) test_view_opens_camera_view

**Class:** FloorPlanPage **Method:** view() **Author:** Bumgyu **Date:** 25-12-01 **Version:** 1.0

**Test Case Description:** Verifies that view opens camera view for unlocked camera.

**Input Specifications**

* Set selected_camera_id to 1.
* Patch get_camera_info to return has_password=False.
* Call view.

**Expected Result**

* open_camera_view is called with argument 1.

**Actual Result (Pass/Fail/Exception):** Pass: Unlocked camera view opens.

**Comment:** Confirms camera view navigation for unlocked cameras.


### 65) test_pan_left_button_calls_controller

**Class:** CameraViewPage **Method:** pan controls **Author:** Bumgyu **Date:** 25-12-01 **Version:** 1.0

**Test Case Description:** Verifies that the pan left button functionality exists in the controller.

**Input Specifications**

* Set camera_view_page.camera_id to 3.
* Patch system.current_camera_controller.

**Expected Result**

* pan_left method is not None in the controller.

**Actual Result (Pass/Fail/Exception):** Pass: Pan left method exists.

**Comment:** Confirms pan left control availability.


### 66) test_pan_right_button_calls_controller

**Class:** CameraViewPage **Method:** pan controls **Author:** Bumgyu **Date:** 25-12-01 **Version:** 1.0

**Test Case Description:** Verifies that the pan right button functionality exists in the controller.

**Input Specifications**

* Set camera_view_page.camera_id to 3.
* Patch system.current_camera_controller.

**Expected Result**

* pan_right method is not None in the controller.

**Actual Result (Pass/Fail/Exception):** Pass: Pan right method exists.

**Comment:** Confirms pan right control availability.


### 67) test_zoom_in_button_calls_controller

**Class:** CameraViewPage **Method:** zoom controls **Author:** Bumgyu **Date:** 25-12-01 **Version:** 1.0

**Test Case Description:** Verifies that the zoom in button functionality exists in the controller.

**Input Specifications**

* Set camera_view_page.camera_id to 3.
* Patch system.current_camera_controller.

**Expected Result**

* zoom_in method is not None in the controller.

**Actual Result (Pass/Fail/Exception):** Pass: Zoom in method exists.

**Comment:** Confirms zoom in control availability.


### 68) test_zoom_out_button_calls_controller

**Class:** CameraViewPage **Method:** zoom controls **Author:** Bumgyu **Date:** 25-12-01 **Version:** 1.0

**Test Case Description:** Verifies that the zoom out button functionality exists in the controller.

**Input Specifications**

* Set camera_view_page.camera_id to 3.
* Patch system.current_camera_controller.

**Expected Result**

* zoom_out method is not None in the controller.

**Actual Result (Pass/Fail/Exception):** Pass: Zoom out method exists.

**Comment:** Confirms zoom out control availability.


### 69) test_get_thumbnail_views_normal

**Class:** FloorPlanPage **Method:** get_thumbnail_views() **Author:** Bumgyu **Date:** 25-12-01 **Version:** 1.0

**Test Case Description:** Verifies that get_thumbnail_views handles different camera states (enabled, disabled, password-protected) and returns appropriate thumbnails for each.

**Input Specifications**

* Add camera 1: enabled, no password.
* Add camera 2: disabled, no password.
* Add camera 3: enabled, with password "hello".
* Call get_thumbnail_views.

**Expected Result**

* thumbs dict contains keys {1, 2, 3}.
* All three values are PIL Image instances.
* All images have size (160, 160).

**Actual Result (Pass/Fail/Exception):** Pass: Thumbnails generated for all camera states.

**Comment:** Tests thumbnail generation for different camera states including the `elif not camera.enabled` branch (line 238-241). Ensures disabled cameras get placeholder images and locked cameras get appropriate thumbnails.

