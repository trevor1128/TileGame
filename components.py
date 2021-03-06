import sfml as sf
import config

class Component(object):
    def __init__(self, sComponentName, bUpdatable, bDrawable):
        #This is here to adapt to the dictionary of components within the Entity instances.
        #This name will be used as the Key for this component.
        self._sName = sComponentName
        self._bUpdatable = bUpdatable
        self._bDrawable = bDrawable

    def _Get_Name(self):
        """This is primarily used for letting the Entity class determine
        the key for the component instance"""
        return self._sName

    def _Get_Updatable(self):
        """For checking to see if this component is updatable."""
        return self._bUpdatable

    def _Get_Drawable(self):
        """For checking to see if this component is drawable."""
        return self._bDrawable
        
class Animated_Sprite(Component):
    #This will be a sprite that can switch its sprite animation according to the state that the parent Entity is in.
    def __init__(self, dData):      #sComponentID, iFrameWidth, iFrameHeight, dTextureStripData):
        Component.__init__(self, "ADSPRITE:%s"%(dData['componentID']), False, True)

        self._bActive = False

        #This will denote the time in-between each frame of the animation in the textures
        self._fDelay = dData['delay']

        #This will tell us when it is time to update the frame.
        self._fAnim_Time = 0.0

        #The current animation is set to its default (which there should be...)
        self._iCurrent_Frame = [0,'DEFAULT']

        self._iFrame_Width = dData['frameWidth']
        self._iFrame_Height = dData['frameHeight']

        #This holds the textures for the animations!
        #It being in a dictionary allows systems to switch to animations easier.
        #Each sAnimation will have a list of the sprite and some data for flexible lengthed animations to be allowed.
        #The list will include [sprite, iFramesWide]    ##only the width is needed because this is a one-dimensional strip (I think this is all we need... Unless we're dealing with LARGE frame dimensions...)
        #self._dAnimated_Sprites = {sAnimation:[sf.Sprite(texture), texture.width/iFrameWidth] for sAnimation, texture in dTextureStripData.items()}

        #Each animation strip gets 
        #for key in self._dAnimated_Sprites.keys():
            #self._dAnimation_Sprites[key][0].set_texture_rect(sf.IntRect(0,0,self._iFrame_Width,self._iFrame_Height))

    def _Activate(self, sStateKey):
        """This will activate a new animation to be played."""
        self._bActive = True

    def _Deactivate(self):
        """This will either halt the animation or make the last frame invisible"""
        self._bActive = False

        #Reload the variables for another activation!
        self._fAnim_Time = 0.0
        self._iCurrent_Frame = [0,0]
        self._Update_Frame()

    def _Update_Frame(self, sAnimation):
        """This simply will be used to update the frame of the animation within the SFML sprite based off of the data in this class."""
        self._dAnimation_Sprites.set_texture_rect(IntRect(self._iCurrent_Frame[0]*self._iFrame_Width,     \
                                                        0,    \
                                                        self._iFrame_Width,                             \
                                                        self._iFrame_Height))

    def _Update(self, timeElapsed):
        pass

class Animation_Sprite(Component):
    #This unlike the Animated_Sprite is a one-shot deal. There will be a varying time until completion (because of differring delays and textureStrip sizes,) but
    #this sprite when triggered will become active (at inactive there isn't an image at all) and render one big animation before becoming inactive again.
    #The idea behind it is that it will be able to play a pretty flexible animation because of the fact that it has no limits on the frames horizontally AND vertically.
    def __init__(self, dData):   #sComponentID, textureGrid, fDelay, iFrameWidth, iFrameHeight, iFramesWide, iFramesHigh):
        Component.__init__(self, "ANSPRITE:%s"%(dData['componentID']), True, True)

        #This animation starts off as inactive and will await a trigger from a system function
        self._bActive = False

        #This will denote the time in-between each frame of the animation in the textureGrid.
        self._fDelay = dData['delay']

        #This will tell us when it is time to update the frame.
        self._fAnim_Time = 0.0

        #The current frame on the texture grid (top-left)
        self._iCurrent_Frame = [0,0]
        
        #The texture grid details 
        self._iFrame_Width = dData['frameWidth']
        self._iFrame_Height = dData['frameHeight']
        self._iFrames_Wide = dData['framesWide']
        self._iFrames_High = dData['framesHigh']

        #This holds the texture for the animation!
        self._Animation_Sprite = sf.Sprite(dData['Texture'][0])

        self._Animation_Sprite.set_texture_rect(sf.IntRect(0,0,self._iFrame_Width, self._iFrame_Height))
        
    def _Activate(self):
        """This will trigger the animation to be played once."""
        self._bActive = True

    def _Deactivate(self):
        """This will either halt the animation or make the last frame invisible"""
        self._bActive = False

        #Reload the variables for another activation!
        self._fAnim_Time = 0.0
        self._iCurrent_Frame = [0,0]
        self._Update_Frame()

    def _Update_Frame(self):
        """This simply will be used to update the frame of the animation within the SFML sprite based off of the data in this class."""
        self._Animation_Sprite.set_texture_rect(IntRect(self._iCurrent_Frame[0]*self._iFrame_Width,     \
                                                        self._iCurrent_Frame[1]*self._iFrame_Height,    \
                                                        self._iFrame_Width,                             \
                                                        self._iFrame_Height))
        
    def _Update(self, timeElapsed):

        if self._bActive:

            #Check to see if the time counter won't reach the end of the animation this update.
            if self._fAnim_Time + timeElapsed < self._iFrame_Width*self._iFrame_Height*self._fDelay:
                #We update our timecounter variable!
                self._fAnim_Time += timeElapsed

                #Check to see if the time counter has passed the delay between the last and upcoming frame update.
                if self._fAnim_Time >= self._fDelay*(self._iCurrent_Frame[1]*self._iFrames_Wide+self._iCurrent_Frame[0]+1): #The +1 will make us check to see if we've reached the NEXT update.
                    #Check to see if we were at the end of the current row last time.
                    if self._iCurrent_Frame[0] + 1 % self._iFrames_Wide:
                        self._iCurrent_Frame[0] = 0

                        if self._iCurrent_Frame[1] + 1 % self._iFrames_High:
                            #The animation is over in terms of the frames...
                            #The game shouldn't get to this point yet, but this'll be here just in case.
                            self._Deactivate()
                            print "The Animation_Sprite component should be deactivating based off of the time counter, not when the frames reach its end!"

                        else:
                            self._iCurrent_Frame[1] += 1

                    else:
                        self._iCurrent_Frame[0] += 1

                    #This will update the frame based off of the information we just altered.
                    self._Update_Frame()
                
            else:
                #The animation is over in term of the time...
                self._Deactivate()

    def _Render(self, renderWindow):

        renderWindow.draw(self._Animation_Sprite)

class Box(Component):
    def __init__(self, dData):  #sComponentID, xPos, yPos, width, height):
        Component.__init__(self, "BOX:%s"%(dData['componentID']), False, True)
        self._box = sf.RectangleShape((int(dData['width']),int(dData['height'])))
        self._box.position = (int(dData['x']),int(dData['y']))
        self._box.fill_color = sf.Color.WHITE
        self._box.outline_color = sf.Color.RED
        self._box.outline_thickness = 3.0

    def _Set_Color(self, fillColor, outlineColor):
        self._box.fill_color = fillColor
        self._box.outline_color = outlineColor

    def _Get_Color(self):
        return self._box.fill_color

    def _Switch_Color(self):
        tmpColor = self._box.fill_color
        self._box.fill_color = self._box.outline_color
        self._box.outline_color = tmpColor

    def _Get_Box(self):
        return self._box

    def _Render(self, renderWindow):
        renderWindow.draw(self._box)
        

class Text_Line(Component):
    def __init__(self, dData):  # sComponentID, xPos, yPos, width, height, text, font):
        Component.__init__(self, "TEXTLINE:%s"%(dData['componentID']), False, True)
        self._text = sf.Text(dData['text'], dData['font'])
        self._text.color = sf.Color.BLACK
        self._text.style = sf.Text.UNDERLINED
        self._text.x = int(dData['x']) + int(dData['width']) / 2.0 - self._text.global_bounds.width / 2.0
        self._text.y = int(dData['y']) + int(dData['height']) / 2.0 - self._text.global_bounds.height / 2.0

    def _Render(self, renderWindow):
        renderWindow.draw(self._text)

class Tile(object):
    """Denotes a single tile within a chunk."""
    def __init__( self ):
        self._is_Active = False    #Tells whether or not the tile is visible or not
        self._tileID = 0           #Identifies the type of tile that is drawn (denotes tile IDs on the tile_atlas.)
        self._tile_AtlasID = 0

    def _Set_TileID(self, iTileID):
        self._tileID = iTileID
        
        #Here we should set the tile_AtlasID also (it's a function of the tileID)

    def _Get_Tile_AtlasID(self):
        return self._tile_AtlasID

    def _Set_Is_Active( self ):
        """Automatically determines if the tile is active or not depending on the tile's type."""
        if self._tileID != 0:
            self._is_Active = True
        else:
            self._is_Active = False

    def __str__( self ):
        """This is the tile's string representation for when it is saved to a file."""
        offset = self._tileID%10    #This will get the first digit for our tileID

        return str((self._tileID-offset)/10) + str(offset)

class List(Component):
    def __init__(self, dData):
        Component.__init__(self, "List:%s"%(dData['componentID']), False, False)
        self._list = []

    def _Add_To_List(self, item):
        self._list.append(item)

    def _Get_Item(self, indx):
        return self._list[indx]


class Flag(Component):
    """This is a piece of logic for Buttons and will tell the button's _box object
    to oscillate its color scheme whenever collisions occur with the mouse and the button."""
    def __init__(self, dData):
        Component.__init__(self, "FLAG:%s"%(dData['componentID']), False, False)
        self._flag = dData['flag']

    def _Set_Flag(self, isActive):
        self._flag = isActive

    def _Get_Flag(self):
        return self._flag


class State(Component):
    def __init__(self, dData):          #sComponentID, sState):
        Component.__init__(self, "STATE:%s"%(dData['componentID']), False, False)
        self._sState = dData['state']

    def _Get_State(self):
        return self._sState

class Position(Component):
    def __init__(self, dData):
        Component.__init__(self, "POS:%s"%(dData['componentID']), False, False)
        self._position = dData['position']

    def _Get_Position(self):
        return self._position

    def _Get_X(self):
        return self._position[0]

    def _Get_Y(self):
        return self._position[1]

    def _Set_Position(self, postion):
        self._position = position


class Misc(Component):
    def __init__(self, dData):
        Component.__init__(self, "MISC:%s"%(dData['componentID']), False, False)
        self._storage = dData['storage']

    def _Set_Storage(self, variable):
        self._storage = variable

    def _Get_Storage(self):
        return self._storage
