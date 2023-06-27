# Trajectory-Planning-2022
### Plan trajectories for autonomous on the fly

## Creating a Trajectory
1. Launch the program - VSCode debug configuration on programming laptop or `python gui.py` when in root directory
2. Select trajectory
   1. Enter the name of the path in place of `default` ie `elevenball` to create a new trajectory
   2. Select an existing trajectory from the dropdown list and press `Load`
3. Creating a path - Select the `New path` button to create a new path. Note - path metadata such as speed is saved automatically after generating a path file or pressing new path
4. Modify data - Note you can only change data for the current path at once. Use the path dropdown to change the selected path
   1. Plot points using left click
   2. Remove points by hovering over them and right-clicking
   3. Drag points by hovering and holding left click
5. When you are ready to make another path, double-check the path metadata is correct and press `New path`
6. When you are ready to generate the data, select the `Generate path file` button. This will close the program and save the data to a `paths.json` config file. It will also create the `.txt` output.

## Known glitches/bugs
* You CAN modify the starting position of a path but CANNOT change the end point. To change this, see the next section 
  * If you want to change the end of a path and the beginning of another, see the next section

## Manually generating data
1. Locate the `modify_traj.py` file found the in the source directory
2. Run `python modify_traj.py` followed by the file name ie `python modify_traj.py fiveball`. Use `-h` for more help
3. To modify a path
   1. Locate the desired `paths.json` file.
   2. Rules
      * The IDs must be zero indexed and consecutive
      * The speed must be in range 10 to -10
      * Point data is stores in feet and must be a floating point number - no negatives
      * The last point of a path must be the first point of the next path
      * Follow JSON formatting structure when adding and removing points
      * The coordinates start in the top left corner of the field near the hanger. Use the GUI program to help orient yourself. If you want you can also multiply any field unit number by approx. 0.02558 to convert from px to feet
