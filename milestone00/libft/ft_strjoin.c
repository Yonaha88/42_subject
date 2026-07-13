/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_strjoin.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: kyonaha <kyonaha@student.42tokyo.jp>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/04/26 16:46:38 by kyonaha           #+#    #+#             */
/*   Updated: 2026/05/01 15:20:18 by kyonaha          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

char	*ft_strjoin(char const *src1, char const *src2)
{
	char	*joined;
	size_t	joined_len;

	if (src1 == NULL && src2 == NULL)
		return (ft_strdup(""));
	if (src1 == NULL)
		return (ft_strdup(src2));
	if (src2 == NULL)
		return (ft_strdup(src1));
	joined_len = ft_strlen(src1) + ft_strlen(src2) + 1;
	joined = (char *)malloc(joined_len * sizeof(char));
	if (joined == NULL)
		return (NULL);
	ft_strlcpy(joined, src1, ft_strlen(src1) + 1);
	ft_strlcat(joined, src2, joined_len);
	return (joined);
}
