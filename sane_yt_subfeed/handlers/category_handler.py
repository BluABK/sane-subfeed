
DEFAULT_CATEGORIES = {
    'Gaming': '#FF0000',
    'Music': '#FFD700',
    'Vlog': '#32CD32',
    'Entertainment': '#9400D3',
    'Education': '#4169E1'
}

CATEGORIES = []


class CategoryObj:
    def __init__(self, name, color):
        self.id = len(CATEGORIES)
        self.name = name
        self.color = color
        self.enabled = True
        self.icon = None
        self.primary_videos = []
        self.videos = []
        self.channels = []

        CATEGORIES.append(self)

    def __repr__(self):
        return "<CategoryObj(id={}, name={}, color={}, enabled={}, icon={}, primary_videos={}, videos={})>".format(
            self.id, self.name, self.color, self.enabled, self.icon, self.primary_videos, self.videos)

    def __str__(self):
        return self.__repr__()

    def add_video(self, video_id, primary=False):
        if primary:
            self.primary_videos.append(video_id)
        else:
            self.videos.append(video_id)

    def add_channel(self, channel_id):
            self.channels.append(channel_id)

    def set_color(self, hexadecimal_str):
        self.color = hexadecimal_str

    def rename(self, new_name):
        self.name = new_name

    def delete(self):
        CATEGORIES.remove(self.id)
        del self


# Set up some default categories
def add_default_categories():
    for category, color in DEFAULT_CATEGORIES.items():
        CategoryObj(category, color)


if __name__ == "__main__":
    add_default_categories()

    for cat_obj in CATEGORIES:
        print(cat_obj)
