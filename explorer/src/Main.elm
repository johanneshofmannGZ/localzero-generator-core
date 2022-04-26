module Main exposing (Model, Msg(..), init, main, subscriptions, update, view)

--import Element.Background as Background

import AllRuns
    exposing
        ( AbsolutePath
        , AllRuns
        , RunId
        )
import Array exposing (Array)
import Browser
import Browser.Dom
import Chart as C
import Chart.Attributes as CA
import Cmd.Extra exposing (withNoCmd)
import CollapseStatus exposing (CollapseStatus, allCollapsed, isCollapsed)
import Dict
import Dropdown
import Element
    exposing
        ( Element
        , alignTop
        , centerX
        , column
        , el
        , fill
        , height
        , minimum
        , padding
        , px
        , row
        , scrollbarY
        , shrink
        , spacing
        , text
        , width
        )
import Element.Background as Background
import Element.Border as Border
import Element.Events as Events
import Element.Font as Font
import Element.Input as Input
import Element.Keyed
import FeatherIcons
import Html exposing (Html)
import Html.Attributes
import Html.Events
import Http
import InterestList exposing (InterestList)
import Json.Decode as Decode
import Json.Encode as Encode
import Maybe.Extra
import Pivot exposing (Pivot)
import Run exposing (Run)
import Set exposing (Set)
import Styling
    exposing
        ( black
        , dangerousIconButton
        , fonts
        , formatGermanNumber
        , germanZeroGreen
        , germanZeroYellow
        , icon
        , iconButton
        , iconButtonStyle
        , modalDim
        , parseGermanNumber
        , red
        , size16
        , sizes
        , treeElementStyle
        , white
        )
import Task
import ValueTree exposing (Node(..), Tree, Value(..))



-- MAIN


main =
    Browser.element
        { init = init
        , update = update
        , subscriptions = subscriptions
        , view = view
        }



-- MODEL


type alias ActiveOverrideEditor =
    { runNdx : RunId, name : String, value : String, asFloat : Maybe Float }


{-| Position of interestlist in pivot
-}
type alias InterestListId =
    Int


type alias Model =
    { runs : AllRuns
    , collapseStatus : CollapseStatus
    , interestLists : Pivot InterestList
    , showModal : Maybe ModalState
    , activeOverrideEditor : Maybe ActiveOverrideEditor
    }


type ModalState
    = PrepareCalculate (Maybe RunId) Run.Inputs Run.Overrides
    | Loading
    | LoadFailure String


encodeOverrides : Run.Overrides -> Encode.Value
encodeOverrides d =
    Encode.dict
        identity
        Encode.float
        d


initiateCalculate : Maybe RunId -> Run.Inputs -> Run.Entries -> Run.Overrides -> Model -> ( Model, Cmd Msg )
initiateCalculate maybeNdx inputs entries overrides model =
    ( { model | showModal = Just Loading }
    , Http.post
        { url = "http://localhost:4070/calculate/" ++ inputs.ags ++ "/" ++ String.fromInt inputs.year
        , expect = Http.expectJson (GotGeneratorResult maybeNdx inputs entries overrides) ValueTree.decoder
        , body = Http.jsonBody (encodeOverrides overrides)
        }
    )


initiateMakeEntries : Maybe RunId -> Run.Inputs -> Run.Overrides -> Model -> ( Model, Cmd Msg )
initiateMakeEntries maybeNdx inputs overrides model =
    ( { model | showModal = Just Loading }
    , Http.get
        { url = "http://localhost:4070/make-entries/" ++ inputs.ags ++ "/" ++ String.fromInt inputs.year
        , expect = Http.expectJson (GotEntries maybeNdx inputs overrides) Run.entriesDecoder
        }
    )


activateInterestList : InterestListId -> Model -> Model
activateInterestList id model =
    { model | interestLists = Pivot.withRollback (Pivot.goTo id) model.interestLists }


init : () -> ( Model, Cmd Msg )
init _ =
    ( { runs = AllRuns.empty
      , showModal = Nothing
      , interestLists = Pivot.singleton InterestList.empty
      , collapseStatus = allCollapsed
      , activeOverrideEditor = Nothing
      }
    , Cmd.none
    )



-- UPDATE


type Msg
    = GotGeneratorResult (Maybe RunId) Run.Inputs Run.Entries Run.Overrides (Result Http.Error Tree)
    | GotEntries (Maybe RunId) Run.Inputs Run.Overrides (Result Http.Error Run.Entries)
      --| AddItemToChartClicked { path : Path, value : Float }
    | AddToInterestList Run.Path
    | AddOrUpdateOverride RunId String Float
    | RemoveOverride RunId String
    | OverrideEdited RunId String String
    | OverrideEditFinished
    | RemoveFromInterestList Run.Path
    | CollapseToggleRequested AbsolutePath
    | UpdateModal ModalMsg
    | DisplayCalculateModalPressed (Maybe RunId) Run.Inputs Run.Overrides
    | CalculateModalOkPressed (Maybe RunId) Run.Inputs
    | RemoveResult RunId
    | ToggleShowGraph InterestListId
    | DuplicateInterestList InterestListId
    | RemoveInterestList InterestListId
    | ActivateInterestList InterestListId
    | Noop


type ModalMsg
    = CalculateModalTargetYearUpdated Int
    | CalculateModalAgsUpdated String


type alias InterestListTable =
    List ( Run.Path, Array Value )


applyInterestListToRuns : InterestList -> AllRuns -> InterestListTable
applyInterestListToRuns interestList runs =
    -- The withDefault handles the case if we somehow managed to get two
    -- differently structured result values into the explorer, this can only
    -- really happen when two different versions of the python code are
    -- explored at the same time.
    -- Otherwise you can't add a path to the interest list that ends
    -- at a TREE
    InterestList.toList interestList
        |> List.map
            (\path ->
                ( path
                , Array.initialize (AllRuns.size runs)
                    (\n ->
                        AllRuns.getValue Run.WithOverrides n path runs
                            |> Maybe.withDefault (String "TREE")
                    )
                )
            )


mapActiveInterestList : (InterestList -> InterestList) -> Model -> Model
mapActiveInterestList f =
    mapInterestLists (Pivot.mapC f)


mapInterestLists : (Pivot InterestList -> Pivot InterestList) -> Model -> Model
mapInterestLists f m =
    { m | interestLists = f m.interestLists }


withLoadFailure : String -> Model -> ( Model, Cmd Msg )
withLoadFailure msg model =
    ( { model | showModal = Just (LoadFailure msg) }, Cmd.none )


update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case msg of
        Noop ->
            model
                |> withNoCmd

        GotEntries maybeNdx inputs overrides (Ok entries) ->
            model
                |> initiateCalculate maybeNdx inputs entries overrides

        GotEntries _ _ _ (Err e) ->
            model
                |> withNoCmd

        GotGeneratorResult maybeNdx inputs entries overrides resultOrError ->
            case resultOrError of
                Ok result ->
                    let
                        run =
                            Run.create
                                { inputs = inputs
                                , entries = entries
                                , result = result
                                , overrides = overrides
                                }

                        newResults =
                            case maybeNdx of
                                Nothing ->
                                    AllRuns.add run model.runs

                                Just ndx ->
                                    AllRuns.set ndx run model.runs
                    in
                    { model
                        | runs = newResults
                        , showModal = Nothing
                    }
                        |> withNoCmd

                Err (Http.BadUrl s) ->
                    model
                        |> withLoadFailure ("BAD URL: " ++ s)

                Err Http.Timeout ->
                    model
                        |> withLoadFailure "TIMEOUT"

                Err Http.NetworkError ->
                    model
                        |> withLoadFailure "NETWORK ERROR"

                Err (Http.BadStatus code) ->
                    model
                        |> withLoadFailure ("BAD STATUS CODE" ++ String.fromInt code)

                Err (Http.BadBody error) ->
                    model
                        |> withLoadFailure ("Failed to decode: " ++ error)

        CollapseToggleRequested path ->
            { model | collapseStatus = CollapseStatus.toggle path model.collapseStatus }
                |> withNoCmd

        RemoveResult ndx ->
            { model | runs = AllRuns.remove ndx model.runs }
                |> withNoCmd

        UpdateModal modalMsg ->
            updateModal modalMsg model.showModal
                |> Tuple.mapFirst (\md -> { model | showModal = md })
                |> Tuple.mapSecond (Cmd.map UpdateModal)

        DisplayCalculateModalPressed maybeNdx inputs overrides ->
            let
                modal =
                    PrepareCalculate maybeNdx inputs overrides
            in
            { model | showModal = Just modal }
                |> withNoCmd

        CalculateModalOkPressed maybeNdx inputs ->
            -- TODO: Actually lookup any existing overrides
            model
                |> initiateMakeEntries maybeNdx inputs Dict.empty

        AddOrUpdateOverride ndx name f ->
            { model
                | runs =
                    model.runs
                        |> AllRuns.update ndx (Run.mapOverrides (Dict.insert name f))
            }
                |> withNoCmd

        OverrideEdited ndx name newText ->
            let
                isFocusChanged =
                    case model.activeOverrideEditor of
                        Nothing ->
                            True

                        Just e ->
                            e.runNdx /= ndx || e.name /= name
            in
            ( { model
                | activeOverrideEditor =
                    Just
                        { runNdx = ndx
                        , name = name
                        , value = newText
                        , asFloat = parseGermanNumber newText
                        }
              }
            , if isFocusChanged then
                Task.attempt (\_ -> Noop) (Browser.Dom.focus "overrideEditor")

              else
                Cmd.none
            )

        OverrideEditFinished ->
            case model.activeOverrideEditor of
                Nothing ->
                    ( model, Cmd.none )

                Just editor ->
                    let
                        modelEditorClosed =
                            { model | activeOverrideEditor = Nothing }
                    in
                    case editor.asFloat of
                        Nothing ->
                            -- Throw the edit away it wasn't valid
                            ( modelEditorClosed, Cmd.none )

                        Just f ->
                            case AllRuns.get editor.runNdx model.runs of
                                Nothing ->
                                    ( modelEditorClosed, Cmd.none )

                                Just run ->
                                    modelEditorClosed
                                        |> initiateMakeEntries (Just editor.runNdx)
                                            (Run.getInputs run)
                                            (Run.getOverrides run
                                                |> Dict.insert editor.name f
                                            )

        RemoveOverride ndx name ->
            { model
                | runs =
                    model.runs
                        |> AllRuns.update ndx (Run.mapOverrides (Dict.remove name))
                , activeOverrideEditor =
                    model.activeOverrideEditor
                        |> Maybe.Extra.filter (\e -> e.runNdx /= ndx || e.name /= name)
            }
                |> withNoCmd

        AddToInterestList path ->
            model
                |> mapActiveInterestList (InterestList.insert path)
                |> withNoCmd

        RemoveFromInterestList path ->
            model
                |> mapActiveInterestList (InterestList.remove path)
                |> withNoCmd

        ToggleShowGraph id ->
            model
                |> activateInterestList id
                |> mapActiveInterestList InterestList.toggleShowGraph
                |> withNoCmd

        DuplicateInterestList id ->
            model
                |> activateInterestList id
                |> mapInterestLists
                    (\p ->
                        Pivot.appendGoR
                            (Pivot.getC p
                                |> InterestList.mapLabel (\l -> l ++ " Copy")
                            )
                            p
                    )
                |> withNoCmd

        RemoveInterestList id ->
            ( model, Cmd.none )

        ActivateInterestList id ->
            model
                |> activateInterestList id
                |> withNoCmd


updateModal : ModalMsg -> Maybe ModalState -> ( Maybe ModalState, Cmd ModalMsg )
updateModal msg model =
    case model of
        Nothing ->
            Nothing
                |> withNoCmd

        Just (PrepareCalculate ndx inputs overrides) ->
            case msg of
                CalculateModalAgsUpdated a ->
                    Just (PrepareCalculate ndx { inputs | ags = a } overrides)
                        |> withNoCmd

                CalculateModalTargetYearUpdated y ->
                    Just (PrepareCalculate ndx { inputs | year = y } overrides)
                        |> withNoCmd

        Just Loading ->
            Just Loading
                |> withNoCmd

        Just (LoadFailure f) ->
            Just (LoadFailure f)
                |> withNoCmd



-- SUBSCRIPTIONS


subscriptions : Model -> Sub Msg
subscriptions model =
    Sub.none



-- VIEW


viewChart : InterestListTable -> Element Msg
viewChart interestList =
    let
        widthChart =
            800

        heightChart =
            600

        bars =
            case interestList of
                [] ->
                    []

                ( _, row ) :: _ ->
                    List.range 0 (Array.length row - 1)
                        |> List.map
                            (\ndx ->
                                let
                                    get ( _, a ) =
                                        case Array.get ndx a of
                                            Just (Float f) ->
                                                f

                                            Just (String _) ->
                                                0.0

                                            Just Null ->
                                                0.0

                                            Nothing ->
                                                0.0
                                in
                                C.bar get []
                                    |> C.named (String.fromInt ndx)
                            )

        chart =
            C.chart
                [ CA.height heightChart
                , CA.width widthChart
                ]
                [ C.xTicks []
                , C.yTicks []
                , C.yLabels []
                , C.xAxis []
                , C.yAxis []
                , C.bars [] bars interestList
                , C.binLabels (String.join "." << Tuple.first) [ CA.moveDown 40 ]
                , C.legendsAt .max
                    .max
                    [ CA.column
                    , CA.moveLeft 5
                    , CA.alignRight
                    , CA.spacing 5
                    ]
                    []
                ]
    in
    el
        [ width (px widthChart)
        , height (px heightChart)
        , padding (2 * sizes.large)
        , alignTop
        , centerX
        ]
        (Element.html chart)


collapsedStatusIcon : AbsolutePath -> CollapseStatus -> Element Msg
collapsedStatusIcon path collapsed =
    let
        i =
            if isCollapsed path collapsed then
                FeatherIcons.chevronRight

            else
                FeatherIcons.chevronDown
    in
    el iconButtonStyle (icon (size16 i))


onEnter : msg -> Element.Attribute msg
onEnter msg =
    Element.htmlAttribute
        (Html.Events.on "keyup"
            (Decode.field "key" Decode.string
                |> Decode.andThen
                    (\key ->
                        if key == "Enter" then
                            Decode.succeed msg

                        else
                            Decode.fail "Not the enter key"
                    )
            )
        )


viewTree :
    Int
    -> Run.Path
    -> CollapseStatus
    -> InterestList
    -> Run.Overrides
    -> Maybe ActiveOverrideEditor
    -> Tree
    -> Element Msg
viewTree resultNdx path collapseStatus interestList overrides activeOverrideEditor tree =
    if isCollapsed ( resultNdx, path ) collapseStatus then
        Element.none

    else
        Dict.toList tree
            |> List.map
                (\( name, val ) ->
                    let
                        isEntry =
                            path == [ "entries" ]

                        itemRow content =
                            row
                                ([ spacing sizes.large, width fill ] ++ treeElementStyle)
                                content

                        childPath =
                            path ++ [ name ]

                        element =
                            case val of
                                Tree child ->
                                    column [ width fill ]
                                        [ Input.button [ width fill, Element.focused [] ]
                                            { label =
                                                itemRow
                                                    [ collapsedStatusIcon ( resultNdx, childPath ) collapseStatus
                                                    , el [ width fill ] (text name)
                                                    , el (Font.alignRight :: fonts.explorerNodeSize) <|
                                                        text (String.fromInt (Dict.size child))
                                                    ]
                                            , onPress = Just (CollapseToggleRequested ( resultNdx, path ++ [ name ] ))
                                            }
                                        , viewTree resultNdx childPath collapseStatus interestList overrides activeOverrideEditor child
                                        ]

                                Leaf Null ->
                                    itemRow
                                        [ el [ width (px 16) ] Element.none
                                        , el [ width fill ] (text name)
                                        , el (Font.alignRight :: Font.bold :: fonts.explorerValues) <| text "null"
                                        ]

                                Leaf (String s) ->
                                    itemRow
                                        [ el [ width (px 16) ] Element.none
                                        , el [ width fill ] (text name)
                                        , el (Font.alignRight :: fonts.explorerValues) <| text s
                                        ]

                                Leaf (Float f) ->
                                    let
                                        formattedF : String
                                        formattedF =
                                            formatGermanNumber f

                                        button =
                                            if InterestList.member childPath interestList then
                                                dangerousIconButton (size16 FeatherIcons.trash2) (RemoveFromInterestList childPath)

                                            else
                                                iconButton (size16 FeatherIcons.plus) (AddToInterestList childPath)

                                        ( originalValue, maybeOverride ) =
                                            -- Clicking on original value should start or revert
                                            -- an override
                                            if isEntry then
                                                let
                                                    override =
                                                        Dict.get name overrides

                                                    thisOverrideEditor =
                                                        activeOverrideEditor
                                                            |> Maybe.Extra.filter (\e -> e.runNdx == resultNdx && e.name == name)

                                                    ( originalStyle, action, o ) =
                                                        case thisOverrideEditor of
                                                            Nothing ->
                                                                case override of
                                                                    Nothing ->
                                                                        ( [ Font.color germanZeroGreen
                                                                          , Element.mouseOver [ Font.color germanZeroYellow ]
                                                                          ]
                                                                        , OverrideEdited resultNdx name formattedF
                                                                        , Element.none
                                                                        )

                                                                    Just newF ->
                                                                        let
                                                                            newFormattedF =
                                                                                formatGermanNumber newF
                                                                        in
                                                                        ( [ Font.strike
                                                                          , Font.color red
                                                                          , Element.mouseOver [ Font.color germanZeroYellow ]
                                                                          ]
                                                                        , RemoveOverride resultNdx name
                                                                        , Input.button (Font.alignRight :: fonts.explorerValues)
                                                                            { label = text newFormattedF
                                                                            , onPress = Just (OverrideEdited resultNdx name newFormattedF)
                                                                            }
                                                                        )

                                                            Just editor ->
                                                                let
                                                                    textStyle =
                                                                        case editor.asFloat of
                                                                            Nothing ->
                                                                                [ Border.color red, Border.width 1 ]

                                                                            Just _ ->
                                                                                [ onEnter OverrideEditFinished
                                                                                ]

                                                                    textAttributes =
                                                                        Events.onLoseFocus OverrideEditFinished
                                                                            :: Element.htmlAttribute (Html.Attributes.id "overrideEditor")
                                                                            :: textStyle
                                                                in
                                                                ( [ Font.strike
                                                                  , Font.color red
                                                                  , Element.mouseOver [ Font.color germanZeroYellow ]
                                                                  ]
                                                                , RemoveOverride resultNdx name
                                                                , Input.text textAttributes
                                                                    { text = editor.value
                                                                    , onChange = OverrideEdited resultNdx name
                                                                    , placeholder = Nothing
                                                                    , label = Input.labelHidden "override"
                                                                    }
                                                                )
                                                in
                                                ( Input.button (Font.alignRight :: fonts.explorerValues ++ originalStyle)
                                                    { label = text formattedF
                                                    , onPress = Just action
                                                    }
                                                , o
                                                )

                                            else
                                                ( el (Font.alignRight :: fonts.explorerValues) <|
                                                    text (formatGermanNumber f)
                                                , Element.none
                                                )
                                    in
                                    itemRow
                                        [ button
                                        , el [ width fill ] (text name)
                                        , originalValue
                                        , maybeOverride
                                        ]
                    in
                    ( name, element )
                )
            |> Element.Keyed.column
                ([ padding sizes.medium
                 , spacing sizes.small
                 , width fill
                 ]
                    ++ fonts.explorerItems
                )


buttons : List (Element Msg) -> Element Msg
buttons l =
    row [ Element.spacingXY sizes.medium 0 ] l


viewInputsAndResult : Int -> CollapseStatus -> InterestList -> Maybe ActiveOverrideEditor -> Run -> Element Msg
viewInputsAndResult resultNdx collapseStatus interestList activeOverrideEditor run =
    let
        inputs =
            Run.getInputs run

        overrides =
            Run.getOverrides run
    in
    column
        [ width fill
        , spacing sizes.medium
        , padding sizes.small
        , Border.width 1
        , Border.color black
        , Border.rounded 4
        ]
        [ row [ width fill ]
            [ Input.button (width fill :: treeElementStyle)
                { label =
                    row [ width fill, spacing sizes.medium ]
                        [ collapsedStatusIcon ( resultNdx, [] ) collapseStatus
                        , el [ Font.bold ] (text (String.fromInt resultNdx ++ ":"))
                        , text (inputs.ags ++ " " ++ String.fromInt inputs.year)
                        ]
                , onPress = Just (CollapseToggleRequested ( resultNdx, [] ))
                }
            , buttons
                [ iconButton FeatherIcons.edit (DisplayCalculateModalPressed (Just resultNdx) inputs overrides)
                , iconButton FeatherIcons.copy (DisplayCalculateModalPressed Nothing inputs overrides)
                , dangerousIconButton FeatherIcons.trash2 (RemoveResult resultNdx)
                ]
            ]
        , viewTree resultNdx
            []
            collapseStatus
            interestList
            overrides
            activeOverrideEditor
            (Run.getTree Run.WithoutOverrides run)
        ]


{-| The pane on the left hand side containing the results
-}
viewResultsPane : Model -> Element Msg
viewResultsPane model =
    column
        [ height fill
        , spacing sizes.large
        , padding sizes.large
        , height (minimum 0 fill)
        , width (minimum 500 shrink)
        ]
        [ el
            [ scrollbarY
            , width fill
            , height fill
            ]
            (column
                [ spacing sizes.large
                , width fill
                , height fill
                ]
                (AllRuns.toList model.runs
                    |> List.map
                        (\( resultNdx, ir ) ->
                            viewInputsAndResult resultNdx
                                model.collapseStatus
                                (Pivot.getC model.interestLists)
                                model.activeOverrideEditor
                                ir
                        )
                )
            )
        ]


viewInterestListTable : InterestListTable -> Element Msg
viewInterestListTable interestList =
    case interestList of
        [] ->
            Element.none

        ( _, row ) :: _ ->
            let
                resultCount =
                    Array.length row

                dataColumns =
                    List.range 0 (resultCount - 1)
                        |> List.map
                            (\resultNdx ->
                                { header = el [ Font.bold, Font.alignRight ] (Element.text (String.fromInt resultNdx))
                                , width = shrink
                                , view =
                                    \( _, values ) ->
                                        let
                                            value =
                                                case Array.get resultNdx values of
                                                    Just (Float f) ->
                                                        el (Font.alignRight :: fonts.explorerValues) <|
                                                            text (formatGermanNumber f)

                                                    Just (String s) ->
                                                        el (Font.alignRight :: fonts.explorerValues) <|
                                                            text s

                                                    Just Null ->
                                                        el (Font.alignRight :: Font.bold :: fonts.explorerValues) <|
                                                            text "bold"

                                                    Nothing ->
                                                        -- make compiler happy
                                                        Element.none
                                        in
                                        value
                                }
                            )

                pathColumn =
                    { header = Element.none, width = shrink, view = \( p, _ ) -> text (String.join "." p) }

                deleteColumn =
                    { header = Element.none
                    , width = shrink
                    , view =
                        \( p, _ ) ->
                            dangerousIconButton (size16 FeatherIcons.trash2) (RemoveFromInterestList p)
                    }
            in
            Element.table
                [ width fill
                , height shrink
                , spacing sizes.large
                , padding sizes.large
                ]
                { data = interestList
                , columns = pathColumn :: dataColumns ++ [ deleteColumn ]
                }


viewInterestList : InterestListId -> Bool -> InterestList -> AllRuns -> Element Msg
viewInterestList id isActive interestList allRuns =
    let
        interestListTable =
            applyInterestListToRuns interestList allRuns

        showGraph =
            InterestList.getShowGraph interestList
    in
    column
        [ width fill
        , Events.onClick (ActivateInterestList id)
        , Element.mouseOver [ Border.color germanZeroYellow ]
        , Border.color
            (if isActive then
                germanZeroYellow

             else
                germanZeroGreen
            )
        , Border.width 1
        , padding sizes.medium
        ]
        [ row
            [ width fill
            , Font.size 24
            , Element.paddingXY sizes.large sizes.medium
            ]
            [ el [ width fill ] (text (InterestList.getLabel interestList))
            , buttons
                [ iconButton
                    (if showGraph then
                        FeatherIcons.eye

                     else
                        FeatherIcons.eyeOff
                    )
                    (ToggleShowGraph id)
                , iconButton FeatherIcons.copy (DuplicateInterestList id)
                , dangerousIconButton FeatherIcons.trash2 Noop
                ]
            ]
        , column [ width fill, spacing 40 ]
            [ if showGraph then
                viewChart interestListTable

              else
                Element.none
            , viewInterestListTable interestListTable
            ]
        ]


viewModel : Model -> Element Msg
viewModel model =
    let
        defaultInputs =
            { ags = ""
            , year = 2035
            }

        topBar =
            row
                ([ width fill
                 , padding sizes.large
                 , Border.color germanZeroYellow
                 , Border.widthEach { bottom = 2, top = 0, left = 0, right = 0 }
                 ]
                    ++ fonts.explorer
                )
                [ text "LocalZero Explorer"
                , el [ width fill ] Element.none
                , iconButton FeatherIcons.plus (DisplayCalculateModalPressed Nothing defaultInputs Dict.empty)
                ]

        interestLists =
            Pivot.indexAbsolute model.interestLists
                |> Pivot.toList
                |> List.map
                    (\( pos, il ) ->
                        let
                            activePos =
                                Pivot.lengthL model.interestLists
                        in
                        viewInterestList pos (pos == activePos) il model.runs
                    )
    in
    column
        [ width fill
        , height fill
        ]
        [ topBar
        , row
            [ width fill
            , height fill
            , spacing sizes.large
            ]
            [ viewResultsPane model
            , column
                [ width fill
                , height fill
                , spacing sizes.medium
                , padding sizes.medium
                ]
                interestLists
            ]
        ]


viewModalDialogBox : Element Msg -> Element Msg
viewModalDialogBox content =
    let
        filler =
            el [ width fill, height fill ] Element.none
    in
    column
        [ width fill
        , height fill
        , Background.color modalDim
        ]
        [ filler
        , row [ width fill, height fill ]
            [ filler
            , el
                [ width (minimum 600 fill)
                , height (minimum 400 fill)
                , Background.color germanZeroYellow
                , Border.rounded 4
                , padding sizes.large
                ]
                content
            , filler
            ]
        , filler
        ]


viewCalculateModal : Maybe Int -> Run.Inputs -> Run.Overrides -> Element Msg
viewCalculateModal maybeNdx inputs overrides =
    let
        labelStyle =
            [ Font.alignRight, width (minimum 100 shrink) ]
    in
    column
        [ width fill
        , height fill
        , Background.color white
        , spacing sizes.medium
        , padding sizes.medium
        ]
        [ Input.text []
            { label = Input.labelLeft labelStyle (text "AGS")
            , text = inputs.ags
            , onChange = UpdateModal << CalculateModalAgsUpdated
            , placeholder = Nothing
            }
        , Input.slider
            [ height (px 20)
            , Element.behindContent
                (el
                    [ width fill
                    , height (px 2)
                    , Element.centerY
                    , Background.color germanZeroGreen
                    , Border.rounded 2
                    ]
                    Element.none
                )
            ]
            { label = Input.labelLeft labelStyle (text (String.fromInt inputs.year))
            , min = 2025
            , max = 2050
            , step = Just 1.0
            , onChange = UpdateModal << CalculateModalTargetYearUpdated << round
            , value = toFloat inputs.year
            , thumb = Input.defaultThumb
            }
        , iconButton FeatherIcons.check (CalculateModalOkPressed maybeNdx inputs)
        ]


view : Model -> Html Msg
view model =
    let
        dialog =
            case model.showModal of
                Nothing ->
                    Element.none

                Just modalState ->
                    viewModalDialogBox
                        (case modalState of
                            PrepareCalculate maybeNdx inputs overrides ->
                                viewCalculateModal maybeNdx inputs overrides

                            Loading ->
                                text "Loading..."

                            LoadFailure msg ->
                                text ("FAILURE: " ++ msg)
                        )
    in
    Element.layout
        [ width fill
        , height fill
        , Element.inFront dialog
        ]
        (viewModel model)
